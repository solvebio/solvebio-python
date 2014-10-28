# -*- coding: utf-8 -*-
"""Handles Querying and Filtering Datasets"""

from .client import client
from .utils.printing import pretty_int
from .utils.tabulate import tabulate

import copy
import logging

logger = logging.getLogger('solvebio')


class Filter(object):
    """
    Filter objects.

    Makes it easier to create filters cumulatively using ``&`` (and),
    ``|`` (or) and ``~`` (not) operations.

    For example::

        f = Filter()
        f &= Filter(price='Free')
        f |= Filter(style='Mexican')

    creates a filter "price = 'Free' or style = 'Mexican'".

    Each set of kwargs in a `Filter` are ANDed together:

      * `<field>='<value>'` matches if the field is that exact value
      * `<field>__in=[<item1>, ...]` matches any of the terms <item1> and so on
      * `<field>__range=[<start>, <end>]` matches anything from <start>
         to <end>
      * `<field>__between=[<start>, <end>]` matches anything between <start> to
         <end> not include either <start> or <end>

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
            f.filters = [self_filters[0]['not']]
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


class PagingQuery(object):
    """
    A Query API request wrapper that generates a request from Filter objects,
    and can iterate through streaming result sets.
    """
    MAXIMUM_LIMIT = 100

    def __init__(self, dataset_id, **params):
        self._dataset_id = dataset_id
        self._data_url = u'/v1/datasets/{0}/data'.format(dataset_id)
        # results per request
        self._limit = int(params.get('limit', PagingQuery.MAXIMUM_LIMIT))
        self._result_class = params.get('result_class', dict)
        self._debug = params.get('debug', False)
        self._fields = params.get('fields', None)
        self._filters = list()

        # init
        self._response = None
        self._reset_iter()
        self._reset_slice_window()

        # parameter error checking
        if self._limit < 0:
            raise Exception('\'limit\' parameter must be >= 0')

    def _clone(self, filters=None):
        new = self.__class__(self._dataset_id,
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
        return self.total

    def __nonzero__(self):
        return bool(len(self))

    def __repr__(self):
        if self.total == 0 or self._limit == 0:
            return u'query returned 0 results'

        return u'\n%s\n\n... %s more results.' % (
            tabulate(self[0].items(), ['Fields', 'Data'],
                     aligns=['right', 'left'], sort=True),
            pretty_int(self.total - 1))

    def _reset_iter(self):
        self._i = -1

    def __getattr__(self, key):
        if self._response is None:
            logger.debug('warmup (__getattr__): %s' % key)
            self.execute()

        if key in self._response:
            return self._response[key]

        raise AttributeError(
            '\'%s\' object has no attribute \'%s\'' %
            (self.__class__.__name__, key))

    def __getitem__(self, key):
        """
        Retrieve an item or slice from the set of results
        """
        self._request_slice = self._as_slice(key)

        # warmup result set...
        if self._response is None:
            logger.debug('warmup (__getitem__): %s' % key)
            self.execute()

        if not isinstance(key, (slice, int, long)):
            raise TypeError
        if self._limit < 0:
            raise ValueError('Indexing not supporting when limit == 0.')
        if isinstance(key, slice):
            key = self._bounded_slice(key)
            start = 0 if key.start is None else key.start
            stop = float('inf') if key.stop is None else key.stop
            if start < 0 or stop < 0 or start > stop:
                raise ValueError('Negative indexing is not supported')
        elif key < 0:
            raise ValueError('Negative indexing is not supported')

        _results = list(self)[:]
        # reset request slice
        self._request_slice = slice(0, float('inf'))
        if isinstance(key, slice):
            _delta = key.stop - key.start
            # slice args must be an integer or None
            if _delta == float('inf'):
                _delta = None
            return _results[slice(0, _delta)]
        else:
            return _results[0]

    def __iter__(self):
        self._reset_iter()
        return self

    def next(self):
        """
        Allows the Query object to be an iterable.
        Iterates through the internal cache using a cursor.
        """
        # increment
        self._i += 1
        return self._next()

    def _next(self):
        _delta = self._request_slice.stop - self._request_slice.start
        if self._i == len(self) or self._i == _delta:
            raise StopIteration()

        i_offset = self._i + self._request_slice.start
        if self._has_slice(self._as_slice(i_offset)):
            _result_start = i_offset - self._window_slice.start
            logger.debug('  window slice: [%s, %s)' %
                         (_result_start, _result_start + 1))
        else:
            logger.debug('executing query. offset/limit: %6d/%d' %
                         (i_offset, self._limit))
            self.execute(offset=i_offset, limit=self._limit)
            _result_start = self._i % self._limit
        return self.results[_result_start]

    # slice operations
    def _as_slice(self, slice_or_idx):
        if isinstance(slice_or_idx, slice):
            return self._bounded_slice(slice_or_idx)
        else:
            return slice(slice_or_idx, slice_or_idx + 1)

    def _bounded_slice(self, _slice):
        return slice(
            _slice.start if _slice.start is not None else 0,
            _slice.stop if _slice.stop is not None else float('inf')
        )

    def _has_slice(self, slice_or_idx):
        return slice_or_idx.start >= self._window_slice.start and \
            slice_or_idx.stop <= self._window_slice.stop

    def _reset_request_slice(self):
        self._request_slice = slice(0, float('inf'))

    def _reset_slice_window(self):
        self._window = []
        self._window_slice = slice(0, float('inf'))
        self._reset_request_slice()

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
        _params = self._build_query()
        _params.update(**params)
        # logger.debug('querying dataset: %s' % str(_params))

        response = client.post(self._data_url, _params)
        logger.debug(
            'query response took: %(took)d ms, total: %(total)d' % response)
        self._response = response

        # update window
        _offset = _params.get('offset', 0)
        _len = len(self._response['results'])
        self._window = self.results
        self._window_slice = slice(_offset, _offset + _len)

        return _params, response


class Query(PagingQuery):
    def __init__(self, dataset_id, **params):
        PagingQuery.__init__(self, dataset_id, **params)

    def __len__(self):
        return min(self.total, len(self.results))

    def _bounded_slice(self, _slice):
        _start = _slice.start
        _stop = _slice.stop
        if _start is None and _stop is None:
            # e.g. q[:] --> [0, limit)
            return slice(0, self._limit)
        elif _start is None:
            # e.g. q[:50] --> [0, min(50, limit) )
            return slice(0, min(_stop, self._limit))
        elif _stop is None:
            # e.g. q[50:] --> [50, 50 + limit)
            return slice(_start, _start + self._limit)
        return slice(_start, _stop)

    def _next(self):
        if self._i == len(self) or self._i == self._limit:
            raise StopIteration()
        return PagingQuery._next(self)

    def __getitem__(self, key):
        if isinstance(key, (int, long)) \
                and key >= self._window_slice.stop:
            raise IndexError()
        return PagingQuery.__getitem__(self, key)


class BatchQuery(object):
    """
    BatchQuery accepts a list of Query objects and executes them
    in a single request to /v1/batch_query.
    """
    def __init__(self, queries):
        """
        Expects a list of Query objects.
        """
        if not isinstance(queries, list):
            queries = [queries]

        self._queries = queries

    def _build_query(self):
        query = {'queries': []}

        for i in self._queries:
            q = i._build_query()
            q.update({'dataset': i._dataset_id})
            query['queries'].append(q)

        return query

    def execute(self, **params):
        _params = self._build_query()
        _params.update(**params)
        response = client.post('/v1/batch_query', _params)
        return response
