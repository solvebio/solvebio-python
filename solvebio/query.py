# -*- coding: utf-8 -*-
from .client import client
from .utils.printing import pretty_int
from .utils.tabulate import tabulate

import abc
import copy
import logging

logger = logging.getLogger('solvebio')
logger.setLevel(logging.DEBUG)


class Filter(object):
    """
    Filter objects.

    Makes it easier to create filters cumulatively using ``&`` (and),
    ``|`` (or) and ``~`` (not) operations.

    For example::

        f = F()
        f &= F(price='Free')
        f |= F(style='Mexican')

    creates a filter "price = 'Free' or style = 'Mexican'".

    Each set of kwargs in a `Filter` are ANDed together:

        * `<field>=''` uses a term filter (exact term)
        * `<field>__in=[]` uses a terms filter (match any)

    String terms are not analyzed and are always assumed to be exact matches.

    Numeric columns can be selected by range using:

        * `<field>__gt`: greater than
        * `<field>__gte`: greater than or equal to
        * `<field>__lt`: less than
        * `<field>__lte`: less than or equal to

    Field action examples:

        dataset.query(gene__in=['BRCA', 'GATA3'],
                      chr='3',
                      start__gt=10000,
                      end__lte=20000)
    """
    def __init__(self, **filters):
        """Creates a Filter"""
        filters = filters.items()
        if len(filters) > 1:
            self.filters = [{'and': filters}]
        else:
            self.filters = filters

    def __repr__(self):
        return '<Filter {0}>'.format(self.filters)

    def _combine(self, other, conn='and'):
        """
        OR and AND will create a new Filter, with the filters from both Filter
        objects combined with the connector `conn`.
        """
        f = Filter()

        self_filters = copy.deepcopy(self.filters)
        other_filters = copy.deepcopy(other.filters)

        if not self.filters:
            f.filters = other_filters
        elif not other.filters:
            f.filters = self_filters
        elif conn in self.filters[0]:
            f.filters = self_filters
            f.filters[0][conn].extend(other_filters)
        elif conn in other.filters[0]:
            f.filters = other_filters
            f.filters[0][conn].extend(self_filters)
        else:
            f.filters = [{conn: self_filters + other_filters}]

        return f

    def __or__(self, other):
        return self._combine(other, 'or')

    def __and__(self, other):
        return self._combine(other, 'and')

    def __invert__(self):
        f = Filter()
        self_filters = copy.deepcopy(self.filters)
        if len(self_filters) == 0:
            # no change
            f.filters = []
        elif (len(self_filters) == 1
              and isinstance(self_filters[0], dict)
              and self_filters[0].get('not', {})):
            # if the filters are already a single dictionary containing a 'not'
            # then swap out the 'not'
            f.filters = self_filters[0]['not']
        else:
            # length of self_filters should never be more than 1
            # 'not' blocks can contain only dicts or a single tuple filter
            # so we get the first element from the filter list
            f.filters = [{'not': self_filters[0]}]

        return f


class RangeFilter(Filter):
    """
    Helper class that generates Range Filters from UCSC-style ranges.
    """
    SUPPORTED_BUILDS = ('hg18', 'hg19', 'hg38')

    @classmethod
    def from_string(cls, string, overlap=False):
        """
        Handles UCSC-style range queries (hg19:chr1:100-200)
        """
        try:
            build, chromosome, pos = string.split(':')
        except ValueError:
            raise ValueError(
                'Please use UCSC-style format: "hg19:chr2:1000-2000"')

        if '-' in pos:
            start, end = pos.replace(',', '').split('-')
        else:
            start = end = pos.replace(',', '')

        return cls(build, chromosome, start, end, overlap=overlap)

    def __init__(self, build, chromosome, start, end, overlap=False):
        """
        Shortcut to do range queries on supported datasets.
        """
        if build.lower() not in self.SUPPORTED_BUILDS:
            raise Exception('Build {0} not supported for range filters. '
                            'Supported builds are: {1}'
                            .format(build, ', '.join(self.SUPPORTED_BUILDS)))

        f = Filter(**{'{0}_start__range'.format(build): [start, end]})

        if overlap:
            f = f | Filter(**{'{0}_end__range'.format(build): [start, end]})
        else:
            f = f & Filter(**{'{0}_end__range'.format(build): [start, end]})

        f = f & Filter(**{'{0}_chromosome'.format(build):
                          str(chromosome).replace('chr', '')})

        self.filters = f.filters

    def __repr__(self):
        return '<RangeFilter {0}>'.format(self.filters)


class QueryBase(object):
    """
    A Query API request wrapper that generates a request from Filter objects,
    and can iterate through streaming result sets.
    """
    __metaclass__ = abc.ABCMeta

    MAXIMUM_LIMIT = 10000

    def __init__(self, data_url, **params):
        self._data_url = data_url
        # results per request
        self._limit = int(params.get('limit', QueryBase.MAXIMUM_LIMIT))
        self._result_class = params.get('result_class', dict)
        self._debug = params.get('debug', False)
        self._fields = params.get('fields', None)
        self._filters = list()

        # response
        self._response = None

        # parameter error checking
        if self._limit < 0:
            raise Exception('"limit" parameter must be >= 0')

    def _clone(self, filters=None):
        new = self.__class__(self._data_url,
                             limit=self._limit,
                             result_class=self._result_class,
                             debug=self._debug)
        new._fields = self._fields
        new._filters += self._filters

        if filters is not None:
            new._filters += filters

        return new

    def filter(self, *filters, **kwargs):
        """
        Returns this Query instance with the query args combined with
        existing set with AND.

        kwargs are simply passed to a new Filter object and combined to any
        other filters with AND.

        By default, everything is combined using AND. If you provide
        multiple filters in a single filter call, those are ANDed
        together. If you provide multiple filters in multiple filter
        calls, those are ANDed together.

        If you want something different, use the F class which supports
        ``&`` (and), ``|`` (or) and ``~`` (not) operators. Then call
        filter once with the resulting Filter instance.
        """
        return self._clone(filters=list(filters) + [Filter(**kwargs)])

    def range(self, chromosome, start, end, strand=None, overlap=True):
        """
        Shortcut to do range queries on supported datasets.
        """
        # TODO: ensure dataset supports range queries?
        return self._clone(
            filters=[RangeFilter(chromosome, start, end, strand, overlap)])

    def _process_filters(self, filters):
        """Takes a list of filters and returns JSON

        :arg filters: list of Filters, (key, val) tuples, or dicts

        :returns: list of JSON API filters
        """
        rv = []
        for f in filters:
            if isinstance(f, Filter):
                if f.filters:
                    rv.extend(self._process_filters(f.filters))
                    continue

            elif isinstance(f, dict):
                key = f.keys()[0]
                val = f[key]

                if isinstance(val, dict):
                    filter_filters = self._process_filters(val)
                    if len(filter_filters) == 1:
                        filter_filters = filter_filters[0]
                    rv.append({key: filter_filters})
                else:
                    rv.append({key: self._process_filters(val)})
            else:
                rv.extend((f,))
        return rv

    def __len__(self):
        return min(self.total, len(self.results))

    def __nonzero__(self):
        return bool(len(self))

    def __repr__(self):
        if self.total == 0 or self._limit == 0:
            return u'Query returned 0 results'

        return u'\n%s\n\n... %s more results.' % (
            tabulate(self[0].items(), ['Fields', 'Data'],
                     aligns=['right', 'left']),
            pretty_int(self.total - 1))

    def __getattr__(self, key):
        if self._response is None:
            logger.debug('Warming up the Query response cache')
            self.execute()

        if key in self._response.keys():
            return self._response[key]

        raise AttributeError(key)

    def __getitem__(self, key):
        """
        Retrieve an item or slice from the set of results
        """
        if not isinstance(key, (slice, int, long)):
            raise TypeError
        if self._limit < 0:
            raise ValueError('Indexing not supporting when limit == 0.')
        if isinstance(key, slice):
            start = 0 if key.start is None else key.start
            stop = float('inf') if key.stop is None else key.stop
            if start < 0 or stop < 0 or start > stop:
                raise ValueError('Negative indexing is not supported')
        elif key < 0:
            raise ValueError('Negative indexing is not supported')

        return self._get_results(key)

    def __iter__(self):
        """
        Execute a query and iterate through the result set.
        Once the cached result set is exhausted, repeat query.
        """
        # always start fresh
        self.execute()
        self._i = -1

        return self

    def next(self):
        """
        Allows the Query object to be an iterable.
        Iterates through the internal cache using a cursor.
        """
        # increment
        self._i += 1

        return self._next()

    @abc.abstractmethod
    def _next(self):
        pass

    @abc.abstractmethod
    def _get_results(self, key):
        pass

    def _build_query(self):
        q = {
            'limit': self._limit,
            'debug': self._debug
        }

        if self._filters:
            filters = self._process_filters(self._filters)
            if len(filters) > 1:
                q['filters'] = [{'and': filters}]
            else:
                q['filters'] = filters

        if self._fields is not None:
            q['fields'] = self._fields

        return q

    def execute(self, **params):
        """
        Executes a query and returns the request parameters and response.
        """
        params.update(self._build_query())
        logger.debug('Querying dataset: %s' % str(params))
        response = client.request('post', self._data_url, params)
        logger.debug('Query response Took %(took)d Total %(total)d' % response)
        self._response = response
        return params, response


class Query(QueryBase):
    def _get_results(self, key):
        return self.results[key]

    def _next(self):
        if self._i == len(self):
            raise StopIteration()

        return self.results[self._i]


# class PagingQuery(QueryBase):
#     def __init__(self, data_url, **params):
#         super(self.__class__, self).__init__(data_url, **params)
#         self._slice = slice(0)

#     def __iter__(self):
#         self._slice = slice(0)
#         return super(self.__class__, self).__iter__()

#     def _next(self):
#         if self._i == self.total:
#             raise StopIteration()

#         if self._i == len(self.results):
#             # fetch next page...
#             _start = self._i / self._limit
#             _stop = _start + self._limit
#             self._slice = slice(_start, _stop)
#             self.execute(offset=_start)

#         return self.results[self._i % self._limit]

#     def _get_results(self, key):
#         if isinstance(key, slice):
#             _key_start = (key.start if isinstance(key, slice) else key) or 0
#             _key_stop = (key.stop if isinstance(key, slice) else key) or self.total
#             key_slice = slice(_key_start, min(_key_stop, _key_start + self._limit))

#             def _in(inner_slice, outer_slice):
#                 return inner_slice.start >= outer_slice.start \
#                             and inner_slice.stop <= outer_slice.stop

#             if not _in(key_slice, self._slice):
#                 self.execute(offset=key_slice.start)
#                 self._slice = slice(key_slice.start, key_slice.start + self._limit)
#             _offset_slice = slice(key_slice.start - self._slice.start, key_slice.stop - self._slice.start)

#             return self.results[_offset_slice]

#         else:
#             if key < self._slice.start or key >= self._slice.stop:
#                 _start = int(key - self._limit*0.5)
#                 _stop = int(key + self._limit*0.5)

#                 # bounds checks...
#                 if _start < 0:
#                     _start = 0
#                     _stop = self._limit
#                 elif _start >= self.total:
#                     _stop = self.total
#                     _start = _stop - self._limit

#                 self.execute(offset=_start)
#                 self._slice = slice(_start, _stop);

#             return self.results[key - self._slice.start]
