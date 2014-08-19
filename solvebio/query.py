# -*- coding: utf-8 -*-
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


class PagingQuery(object):
    """
    A Query API request wrapper that generates a request from Filter objects,
    and can iterate through streaming result sets.
    """
    MAXIMUM_LIMIT = 10000

    def __init__(self, data_url, **params):
        self._data_url = data_url
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

        # cache
        self._cache = []
        self._cached_slice = slice(0)

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
        return self.total

    def __nonzero__(self):
        return bool(len(self))

    def __repr__(self):
        if self.total == 0 or self._limit == 0:
            return u'query returned 0 results'

        return u'\n%s\n\n... %s more results.' % (
            tabulate(self[0].items(), ['Fields', 'Data'],
                     aligns=['right', 'left']),
            pretty_int(self.total - 1))

    def _reset_iter(self):
        self._response = None
        self._i = -1

    def __getattr__(self, key):
        if self._response is None:
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
        self._reset_iter()
        if self._slice_window is None:
            self._slice_window = slice(0, float('inf'))
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
        _delta = (self._slice_window.stop - self._slice_window.start)
        if self._i == self.total or self._i == _delta:
            raise StopIteration()

        if self._i == 0 or self._i % len(self.results) == 0:
            # fetch next page...
            _start = (self._i / self._limit) * self._limit + \
                self._slice_window.start
            # define '_stop' for debugging only!
            _stop = self._slice_window.stop
            _limit = min(_stop - _start, self._limit)
            logger.debug('executing query. offset/limit: %6d/%d' %
                        (_start, _limit))
            self.execute(offset=_start, limit=_limit)

            # update cache
            self._cache = self.results
            self._cached_slice = slice(
                self._slice_window.start, self._slice_window.stop)

        return self.results[self._i % self._limit]

    # slice operations
    def _as_slice(self, slice_or_idx):
        if isinstance(slice_or_idx, slice):
            return slice_or_idx
        else:
            return slice(slice_or_idx, slice_or_idx + 1)

    def _has_slice(self, slice_or_idx):
        return slice_or_idx.start >= self._cached_slice.start and \
            slice_or_idx.stop <= self._cached_slice.stop

    def _set_slice_window(self, _slice):
        _start = _slice.start
        _stop = _slice.stop

        # expand slice around requested range
        _delta = _stop - _start
        _width = max(min(self._limit, 100), _delta)
        _start = _start - (_width - _delta) / 2
        _stop = _start + _width
        if _start <= 0:
            _start = 0
            _stop = _width
        elif _stop >= self.total:
            _start = self.total - _width
            _stop = self.total

        # update slice window
        self._slice_window = slice(_start, _stop)

        # update slice result offset
        self._slice_result_offset = slice(
            _slice.start - _start, _slice.stop - _start)

    def _reset_slice_window(self):
        self._slice_window = slice(0, float('inf'))
        self._slice_query = slice(0, float('inf'))
        self._slice_result_offset = slice(0, float('inf'))

    def _get_results(self, key):
        is_slice = isinstance(key, slice)

        key = self._as_slice(key)
        self._slice_query = slice(key.start, key.stop)

        logger.debug('fetching slice: [%s, %s)' % (key.start, key.stop))

        if self._has_slice(key):
            _cache_start = key.start - self._cached_slice.start
            _cache_stop = (key.stop - key.start) + _cache_start
            _cached_slice = slice(_cache_start, _cache_stop)
            logger.debug('  cached slice: [%s, %s)' %
                        (_cached_slice.start, _cached_slice.stop))
            return self._cache[_cached_slice] \
                if is_slice else self._cache[_cache_start]

        self._set_slice_window(key)
        results = list(self)[self._slice_result_offset]
        self._reset_slice_window()
        return results if is_slice else results[0]

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
        response = client.request('post', self._data_url, _params)
        logger.debug(
            'query response took: %(took)d ms, total: %(total)d' % response)
        self._response = response
        return _params, response


# TODO: fix Python module reload bug that's breaking "super"
class Query(PagingQuery):
    def __init__(self, data_url, **params):
        super(self.__class__, self).__init__(data_url, **params)

    def __len__(self):
        return min(self.total, len(self.results))

    def _next(self):
        _delta = (self._slice_query.stop - self._slice_query.start)
        if self._i == self.total or self._i == _delta:
            raise StopIteration()

        return super(self.__class__, self)._next()
