# -*- coding: utf-8 -*-
"""Handles Querying and Filtering Datasets"""
from itertools import islice

from .client import client
from .cursor import Cursor
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


# slice utils
def bounded_slice(_slice):
    return slice(
        _slice.start if _slice.start is not None else 0,
        _slice.stop if _slice.stop is not None else float('inf')
    )


def as_slice(slice_or_idx):
    if isinstance(slice_or_idx, slice):
        return bounded_slice(slice_or_idx)
    else:
        return slice(slice_or_idx, slice_or_idx + 1)


class Query(object):
    """
    A Query API request wrapper that generates a request from Filter objects,
    and can iterate through streaming result sets.
    """

    # The maximum number of results fetched in one go. Note however
    # that iterating over a query can cause more fetches.
    DEFAULT_PAGE_SIZE = 1000

    def __init__(
            self,
            dataset_id,
            result_class=dict,
            fields=None,
            filters=None,
            limit=float('inf'),
            page_size=DEFAULT_PAGE_SIZE,
            genome_build=None):
        """
        Creates a new Query object.

        :Parameters:
          - `dataset_id`: Unique ID of dataset to query.
          - `genome_build`: The genome build to use for the query.
          - `result_class` (optional): Class of object returned by query.
          - `fields` (optional): List of specific fields to retrieve.
          - `filters` (optional): List of filter objects.
          - `limit` (optional): Maximum number of query results to return.
          - `page_size` (optional): Number of results to fetch per query page.
        """
        self._dataset_id = dataset_id
        self._genome_build = genome_build
        self._data_url = u'/v1/datasets/{0}/data'.format(dataset_id)
        self._limit = limit
        self._result_class = result_class
        self._fields = fields
        if filters:
            if isinstance(filters, Filter):
                filters = [filters]
        else:
            filters = []
        self._filters = filters

        # init response and cursor
        self._response = None
        self._cursor = Cursor(0, -1, 0)
        self._page_size = int(page_size)

        # parameter error checking
        if self._limit < 0:
            raise Exception('\'limit\' parameter must be >= 0')

    def _clone(self, filters=None):
        new = self.__class__(self._dataset_id,
                             genome_build=self._genome_build,
                             limit=self._limit,
                             result_class=self._result_class)
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

    def count(self):
        """
        Returns the total number of results returned by a query.
        The count is dependent on the filters, but independent of any limit.
        It is like SQL:
           SELECT COUNT(*) FROM <depository> [WHERE condition].
        See also __len__ for a function that is dependent on limit.
        """
        # clone self and query with limit = 0 to get total
        query_clone = self._clone()
        query_clone._limit = 0
        return query_clone.total

    def _process_filters(self, filters):
        """Takes a list of filters and returns JSON

        :Parameters:
        - `filters`: List of Filters, (key, val) tuples, or dicts

        Returns: List of JSON API filters
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
        """
        Returns the total number of results returned in a query. It is the
        number of items you can iterate over.

        In contrast to count(), the result does take into account any limit
        given. In SQL it is like:

              SELECT COUNT(*) FROM (
                 SELECT * FROM <table> [WHERE condition] [LIMIT number]
              )
        """
        return min(self._limit, self.total)

    def __nonzero__(self):
        return bool(len(self))

    def __repr__(self):
        if len(self) == 0:
            return u'Query returned 0 results.'

        return u'\n%s\n\n... %s more results.' % (
            tabulate(self[0].items(), ['Fields', 'Data'],
                     aligns=['right', 'left'], sort=True),
            pretty_int(self.total - 1))

    def __getattr__(self, key):
        if self._response is None:
            logger.debug('warmup (__getattr__: %s)' % key)
            self.execute()

        if key in self._response:
            return self._response[key]

        raise AttributeError(
            '\'%s\' object has no attribute \'%s\'' %
            (self.__class__.__name__, key))

    def __getitem__(self, key):
        """
        Retrieve an item or slice from the result set.

        Query's do not support negative indexing.

        :Parameters:
        - `key`: The requested slice range or index.
        """
        # validate type
        if not isinstance(key, (slice, int, long)):
            raise TypeError

        # validate not negative indexing
        if isinstance(key, slice):
            key = bounded_slice(key)
            start = 0 if key.start is None else key.start
            stop = float('inf') if key.stop is None else key.stop
            if start < 0 or stop < 0 or start > stop:
                raise ValueError('Negative indexing is not supported')

        elif key < 0:
            raise ValueError('Negative indexing is not supported')

        # Reset the cursor offset so that it is internally referencing
        # the start of the requested key. If the offset is out of bounds
        # (i.e. less than 0 or greater than cursor stop) the query will
        # request a new result page (see: next())
        self._cursor.reset_absolute(as_slice(key).start)

        # cursor.offset_absolute is now key.start (if slice) or key (if int)
        if isinstance(key, slice):
            _delta = key.stop - key.start

            if _delta == float('inf'):
                _delta = None

            # return list
            return list(islice(self, _delta))

        # return single element
        return list(islice(self, 1))[0]

    def __iter__(self):
        return self

    def next(self):
        """
        Allows the Query object to be an iterable.

        This method will iterate through a cached result set
        and fetch successive pages as required.

        A `StopIteration` exception will be raised when there aren't
        any more results available or when the requested result
        slice range or limit has been fetched.

        Returns: The next result.
        """
        # prevents an additional query when requesting a slice
        #  range that is out of bounds (i.e. results[limit:])
        if self._cursor.offset_absolute >= self._limit:
            raise StopIteration()

        if self._cursor.has_next():
            _result_start = self._cursor.offset
            logger.debug('page slice: [%s, %s)' %
                         (_result_start, _result_start + 1))

        else:
            self.execute()
            # reset page index
            _result_start = 0

        # if no results when fetching next page, terminate
        if len(self.results) == 0:
            raise StopIteration()

        # increment page index
        self._cursor.advance()

        return self.results[_result_start]

    def _build_query(self, **kwargs):
        q = {}

        if self._filters:
            filters = self._process_filters(self._filters)
            if len(filters) > 1:
                q['filters'] = [{'and': filters}]
            else:
                q['filters'] = filters

        if self._fields is not None:
            q['fields'] = self._fields

        if self._genome_build is not None:
            q['genome_build'] = self._genome_build

        # Add or modify query parameters (used by BatchQuery)
        q.update(**kwargs)

        return q

    def execute(self):
        """
        Executes a query.

        Returns: The request parameters and the raw query response.
        """
        _params = self._build_query()

        offset = self._cursor.offset_absolute
        limit = min(self._page_size,
                    self._limit - self._cursor.offset_absolute)

        _params.update(
            offset=offset,
            limit=limit
        )

        logger.debug('executing query. from/limit: %6d/%d' %
                     (offset, limit))
        response = client.post(self._data_url, _params)
        logger.debug(
            'query response took: %(took)d ms, total: %(total)d' % response)

        self._response = response

        # reset cursor if have results
        self._cursor.reset(offset, offset + limit, 0)

        return _params, response


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
            _params = i._build_query(
                offset=i._cursor.offset_absolute,
                limit=min(i._page_size, i._limit - i._cursor.offset_absolute),
                dataset=i._dataset_id
            )
            query['queries'].append(_params)

        return query

    def execute(self, **params):
        _params = self._build_query()
        _params.update(**params)
        response = client.post('/v1/batch_query', _params)
        return response
