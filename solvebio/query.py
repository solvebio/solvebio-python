# -*- coding: utf-8 -*-
from __future__ import absolute_import

from abc import ABCMeta

import six
import json
import uuid

from .client import client
from .utils.printing import pretty_int
from .utils.tabulate import tabulate
from .errors import SolveError

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
    def __init__(self, *raw_filters, **filters):
        """Creates a Filter"""
        # Set deepcopy to False for faster Filter building
        self.deepcopy = True

        filters = list(filters.items())
        for flt in raw_filters:
            try:
                flt = json.loads(flt)
                # If the result is a dict, wrap in a list.
                if isinstance(flt, dict):
                    flt = [flt]
            except:
                raise Exception(
                    'Invalid raw filter, must be a JSON string: {}'
                    .format(flt))

            filters += flt

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
        f.deepcopy = self.deepcopy and other.filters

        if f.deepcopy:
            self_filters = copy.deepcopy(self.filters)
            other_filters = copy.deepcopy(other.filters)
        else:
            self_filters = self.filters
            other_filters = other.filters

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
        f.deepcopy = self.deepcopy

        if f.deepcopy:
            self_filters = copy.deepcopy(self.filters)
        else:
            self_filters = self.filters

        if len(self.filters) == 0:
            # no change
            f.filters = []
        elif (len(self.filters) == 1 and
              isinstance(self.filters[0], dict) and
              self.filters[0].get('not', {})):
            # if the filters are already a single dictionary containing a 'not'
            # then swap out the 'not'
            f.filters = [self_filters[0]['not']]
        else:
            # length of self.filters should never be more than 1
            # 'not' blocks can contain only dicts or a single tuple filter
            # so we get the first element from the filter list
            f.filters = [{'not': self_filters[0]}]

        return f


class GenomicFilter(Filter):
    """
    Helper class that generates filters on genomic coordinates.

    Range filtering only works on "genomic" datasets
    (where dataset.is_genomic is True).
    """
    # Standardized fields for genomic coordinates in SolveBio
    FIELD_START = 'genomic_coordinates.start'
    FIELD_STOP = 'genomic_coordinates.stop'
    FIELD_CHR = 'genomic_coordinates.chromosome'

    @classmethod
    def from_string(cls, string, exact=False):
        """
        Handles UCSC-style range queries (chr1:100-200)
        """
        try:
            chromosome, pos = string.split(':')
        except ValueError:
            raise ValueError('Please use UCSC-style format: "chr2:1000-2000"')

        if '-' in pos:
            start, stop = pos.replace(',', '').split('-')
        else:
            start = stop = pos.replace(',', '')

        return cls(chromosome, start, stop, exact=exact)

    def __init__(self, chromosome, start, stop=None, exact=False):
        """
        This class supports single position and range filters.

        By default, the filter will match any record that overlaps with
        the position or range specified. Exact matches must be explicitly
        specified using the `exact` parameter.
        """
        try:
            # Allows start=None to filter items with no position
            if start is not None:
                start = int(start)

            if stop is None:
                stop = start
            else:
                stop = int(stop)
        except ValueError:
            raise ValueError(
                'Start and stop positions must be integers (or None)')

        if exact or start is None:
            # Handle the case where start is None because sometimes
            # a record will have only the chromosome set (no positions).
            f = Filter(**{self.FIELD_START: start, self.FIELD_STOP: stop})
        else:
            f = Filter(**{self.FIELD_START + '__lte': start,
                          self.FIELD_STOP + '__gte': stop})
            if start != stop:
                f = f | Filter(**{self.FIELD_START + '__range':
                                  [start, stop]})
                f = f | Filter(**{self.FIELD_STOP + '__range':
                                  [start, stop]})

        if chromosome is None:
            f = f & Filter(**{self.FIELD_CHR: None})
        else:
            f = f & \
                Filter(**{self.FIELD_CHR: str(chromosome).replace('chr', '')})
        self.filters = f.filters

    def __repr__(self):
        return '<GenomicFilter {0}>'.format(self.filters)


@six.add_metaclass(ABCMeta)
class QueryBase(object):
    """
    A helper abstract mixin class that contains
    common methods for Query and QueryFile classes.
    """

    # The maximum number of results fetched in one go.
    DEFAULT_PAGE_SIZE = 100

    # INF represents an integer version of 'float('inf')'
    # because it could not be typecasted to integer
    INF = 10 ** 15

    # Special case for Query/QueryFile class to pre-set SolveClient
    _client = None

    def limit(self, limit):
        """
        Returns a new Query/QueryFile instance with the new
        limit values.
        """
        return self._clone(limit=limit)

    def count(self):
        """
        Returns the total number of results returned by a query.
        The count is dependent on the filters, but independent of any limit.
        It is like SQL:
           SELECT COUNT(*) FROM <table> [WHERE condition].
        See also __len__ for a function that is dependent on limit.
        """
        # self.total will warm up the response if it needs to
        return self.total

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
        return min(self._limit, self.count()) if not self.count() is None else self._limit

    def __nonzero__(self):
        return bool(len(self))

    @property
    def _buffer(self):
        if self._response is None:
            logger.debug('warmup (buffer)')
            self.execute(self._slice.start if self._slice else 0)
        return self._response['results']

    def __repr__(self):
        # Check that Query/QueryFile object does not have any previous errors
        # otherwise, raise the error.
        if self._error:
            raise self._error

        if len(self) == 0:
            return 'Query returned 0 results.'

        return '\n%s\n\n... %s more results.' % (
            tabulate(list(self._buffer[0].items()), ['Fields', 'Data'],
                     aligns=['right', 'left'], sort=True),
            pretty_int(len(self) - 1))

    def __getattr__(self, key):
        if self._response is None:
            logger.debug('warmup (__getattr__: %s)' % key)
            self.execute(self._slice.start if self._slice else 0)

        # Check that Query/QueryFile object does not have any previous errors
        # otherwise, raise the error.
        # execute() sets the error, so the check is placed after it.
        if self._error:
            raise self._error

        if key in self._response:
            return self._response[key]

        raise AttributeError(
            '\'%s\' object has no attribute \'%s\'' %
            (self.__class__.__name__, key))

    @staticmethod
    def bounded_slice(_slice):
        return slice(
            _slice.start if _slice.start is not None else 0,
            _slice.stop if _slice.stop is not None else float('inf')
        )

    @staticmethod
    def as_slice(slice_or_idx):
        if isinstance(slice_or_idx, slice):
            return QueryBase.bounded_slice(slice_or_idx)
        return slice(slice_or_idx, slice_or_idx + 1)

    def __getitem__(self, key):
        """
        Retrieve an item or slice from the result set.

        Query/QueryFile's do not support negative indexing.

        :Parameters:
        - `key`: The requested slice range or index.
        """
        if not isinstance(key, (slice,) + six.integer_types):
            raise TypeError

        if isinstance(key, slice):
            key = QueryBase.bounded_slice(key)
            start = 0 if key.start is None else key.start
            stop = float('inf') if key.stop is None else key.stop

            if start < 0 or stop < 0 or start > stop:
                raise ValueError('Negative indexing is not supported')

            # If a slice is already set, the new slice should be relative
            if self._slice:
                start += self._slice.start
                stop = min(self._slice.start + stop, self._slice.stop)
                # Make sure the new relative start position is within
                # the previous slice.
                if start >= self._slice.stop:
                    return []

            # We need to make a few requests to get the data.
            # We should respect the user's limit if it is smaller than slice.
            # To prevent the state of page_size/offset from being stored,
            # we'll clone this object first.
            q = self._clone()
            q._limit = min(stop - start, self._limit)
            # Setting slice will signal to the iter methods the page_offset.
            q._slice = slice(start, stop)
            return q

        # Not a slice (key is an int)
        if key < 0:
            raise ValueError('Negative indexing is not supported')

        # If a slice already exists, the key is relative to that slice
        if self._slice:
            key = key + self._slice.start
            if key >= self._slice.stop:
                raise IndexError('list index out of range')

        # Use key as the new page_offset and fetch a new page of results
        q = self._clone()
        q._limit = min(1, self._limit)  # Limit may be 0
        q.execute(key)
        return q._buffer[0]

    def __iter__(self):
        # e.g. [r for r in results] will NOT call __getitem__ and
        # requires that we start iteration from the 0th element
        self.execute(self._slice.start if self._slice else 0)

        # Reset the cursor
        self._cursor = 0  # Count the number of results returned
        self._buffer_idx = 0  # The current position within the buffer

        return self

    def __next__(self):
        """Python 3"""
        return self.next()

    def next(self):
        """
        Allows the Query/QueryFile object to be an iterable.

        This method will iterate through a cached result set
        and fetch successive pages as required.

        A `StopIteration` exception will be raised when there aren't
        any more results available or when the requested result
        slice range or limit has been fetched.

        Returns: The next result.
        """
        if not hasattr(self, '_cursor'):
            # Iterator not initialized yet
            self.__iter__()

        # len(self) returns `min(limit, total)` results
        if self._cursor == len(self):
            raise StopIteration

        if self._buffer_idx == len(self._buffer):
            self.execute(self._page_offset + self._buffer_idx)
            self._buffer_idx = 0

        if not self._buffer:
            raise StopIteration

        self._cursor += 1
        self._buffer_idx += 1

        return self._buffer[self._buffer_idx - 1]

    def filter(self, *filters, **kwargs):
        """
        Returns this Query/QueryFile instance with the query args combined with
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
        f = list(filters)

        if kwargs:
            f += [Filter(**kwargs)]

        return self._clone(filters=f)

    @classmethod
    def _process_filters(cls, filters):
        """Takes a list of filters and returns JSON

        :Parameters:
        - `filters`: List of Filters, (key, val) tuples, or dicts

        Returns: List of JSON API filters
        """
        data = []

        # Filters should always be a list
        for f in filters:
            if isinstance(f, Filter):
                if f.filters:
                    data.extend(cls._process_filters(f.filters))
            elif isinstance(f, dict):
                key = list(f.keys())[0]
                val = f[key]

                if isinstance(val, dict):
                    # pass val (a dict) as list
                    # so that it gets processed properly
                    filter_filters = cls._process_filters([val])
                    if len(filter_filters) == 1:
                        filter_filters = filter_filters[0]
                    data.append({key: filter_filters})
                else:
                    data.append({key: cls._process_filters(val)})
            else:
                data.extend((f,))

        return data


class Query(QueryBase):
    """
    A Query API request wrapper that generates a request from Filter objects,
    and can iterate through streaming result sets.
    """

    def __init__(
            self,
            dataset_id,
            query=None,
            genome_build=None,
            filters=None,
            fields=None,
            exclude_fields=None,
            entities=None,
            ordering=None,
            limit=float('inf'),
            page_size=QueryBase.DEFAULT_PAGE_SIZE,
            result_class=dict,
            target_fields=None,
            annotator_params=None,
            debug=False,
            error=None,
            **kwargs):
        """
        Creates a new Query object.

        :Parameters:
          - `dataset_id`: Unique ID of dataset to query.
          - `query` (optional): An optional query string.
          - `genome_build`: The genome build to use for the query.
          - `result_class` (optional): Class of object returned by query.
          - `fields` (optional): List of specific fields to retrieve.
          - `exclude_fields` (optional): List of specific fields to exclude.
          - `entities` (optional): List of entity tuples to filter on.
          - `ordering` (optional): List of fields to order the results by.
          - `filters` (optional): Filter or List of filter objects.
          - `limit` (optional): Maximum number of query results to return.
          - `page_size` (optional): Number of results to fetch per query page.
          - `target_fields` (optional): Add target fields to annotate the query results.
          - `annotator_params` (optional): For use with `target_fields` to adjust annotator parameters.
          - `debug` (optional): Sends debug information to the API.
        """
        self._dataset_id = dataset_id
        self._data_url = '/v2/datasets/{0}/data'.format(dataset_id)
        self._query = query
        self._genome_build = genome_build
        self._result_class = result_class
        self._fields = fields
        self._exclude_fields = exclude_fields
        self._entities = entities
        self._ordering = ordering
        self._debug = debug
        self._error = error
        self._target_fields = target_fields
        self._annotator_params = annotator_params
        if filters:
            if isinstance(filters, Filter):
                filters = [filters]
        else:
            filters = []
        self._filters = filters

        # init response and cursor
        self._response = None
        # Limit defines the total number of results that will be returned
        # from a query involving 1 or more pagination requests.
        self._limit = limit
        # Page size/offset are the low level API limit and offset params.
        self._page_size = int(page_size)
        # Page offset can only be set by execute(). It is always set to the
        # current absolute offset contained in the buffer.
        self._page_offset = None
        # slice is set when the Query is being sliced.
        # In this case, __iter__() and next() will not
        # reset the page_offset to 0 before iterating.
        self._slice = None

        # parameter error checking
        if self._limit < 0:
            raise Exception('\'limit\' parameter must be >= 0')

        if self._page_size <= 0:
            raise Exception('\'page_size\' parameter must be > 0')

        # Set up the SolveClient
        # (kwargs overrides pre-set, which overrides global)
        self._client = kwargs.get('client') or self._client or client

    def _clone(self, filters=None, limit=None):
        new = self.__class__(self._dataset_id,
                             query=self._query,
                             genome_build=self._genome_build,
                             limit=self._limit,
                             fields=self._fields,
                             exclude_fields=self._exclude_fields,
                             entities=self._entities,
                             ordering=self._ordering,
                             page_size=self._page_size,
                             result_class=self._result_class,
                             target_fields=self._target_fields,
                             annotator_params=self._annotator_params,
                             debug=self._debug,
                             client=self._client)
        new._filters += self._filters

        if filters:
            new._filters += filters

        if limit:
            new._limit = limit

        return new

    def range(self, chromosome, start, stop, exact=False):
        """
        Shortcut to do range filters on genomic datasets.
        """
        return self._clone(
            filters=[GenomicFilter(chromosome, start, stop, exact)])

    def position(self, chromosome, position, exact=False):
        """
        Shortcut to do a single position filter on genomic datasets.
        """
        return self._clone(
            filters=[GenomicFilter(chromosome, position, exact=exact)])

    def facets(self, *args, **kwargs):
        """
        Returns a dictionary with the requested facets.

        The facets function supports string args, and keyword
        args.

        q.facets('field_1', 'field_2') will return facets for
        field_1 and field_2.
        q.facets(field_1={'limit': 0}, field_2={'limit': 10})
        will return all facets for field_1 and 10 facets for field_2.
        """
        # Combine args and kwargs into facet format.
        facets = dict((a, {}) for a in args)
        facets.update(kwargs)

        if not facets:
            raise AttributeError('Faceting requires at least one field')

        for f in facets.keys():
            if not isinstance(f, six.string_types):
                raise AttributeError('Facet field arguments must be strings')

        q = self._clone()
        q._limit = 0
        q.execute(offset=0, facets=facets)
        return q._response.get('facets')

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
        if getattr(self, '_is_join', False):
            return len(self._buffer)

        return super(Query, self).__len__()

    def _build_query(self, **kwargs):
        q = {}

        if self._query:
            q['query'] = self._query

        if self._filters:
            filters = self._process_filters(self._filters)
            if len(filters) > 1:
                q['filters'] = [{'and': filters}]
            else:
                q['filters'] = filters

        if self._fields is not None:
            q['fields'] = self._fields

        if self._exclude_fields is not None:
            q['exclude_fields'] = self._exclude_fields

        if self._entities is not None:
            q['entities'] = self._entities

        if self._ordering is not None:
            q['ordering'] = self._ordering

        if self._genome_build is not None:
            q['genome_build'] = self._genome_build

        if self._debug:
            q['debug'] = 'True'

        if self._target_fields:
            q['target_fields'] = self._target_fields

        if self._annotator_params:
            q['annotator_params'] = self._annotator_params

        # Add or modify query parameters
        # (used by BatchQuery and facets)
        q.update(**kwargs)

        return q

    def execute(self, offset=0, **query):
        """
        Executes a query. Additional query parameters can be passed
        as keyword arguments.

        Returns: The request parameters and the raw query response.
        """
        _params = self._build_query(**query)
        self._page_offset = offset

        _params.update(
            offset=self._page_offset,
            limit=min(self._page_size, self._limit)
        )

        logger.debug('executing query. from/limit: %6d/%d' %
                     (_params['offset'], _params['limit']))

        # If the request results in a SolveError (ie bad filter) set the error.
        try:
            self._response = self._client.post(self._data_url, _params)
        except SolveError as e:
            self._error = e
            raise

        logger.debug('query response took: %(took)d ms, total: %(total)d'
                     % self._response)
        return _params, self._response

    def fields(self):
        """Returns all expected fields that will be found in the results."""

        from solvebio import Dataset

        fields = [f for f in Dataset(self._dataset_id, client=self._client).fields()]
        if self._fields:
            fields = [f for f in fields if f.name in self._fields]
        if self._exclude_fields:
            fields = [f for f in fields if f.name not in self._exclude_fields]

        return fields

    def export(self, format='json', follow=True, limit=None, **kwargs):
        from solvebio import DatasetExport

        params = self._build_query()
        params.pop('offset', None)
        params.pop('ordering', None)

        # if limit is not set use max limit
        if not limit and self._limit < float('inf'):
            limit = self._limit

        if limit:
            params['limit'] = limit

        # target_fields and annotator_params must be passed
        # directly into the migration.
        # Prefer explicitly passed-in values before query values.
        target_fields = kwargs.pop('target_fields', None) or \
            params.pop('target_fields', None)
        annotator_params = kwargs.pop('annotator_params', None) or \
            params.pop('annotator_params', None)

        export = DatasetExport.create(
            dataset_id=self._dataset_id,
            format=format,
            params=params,
            target_fields=target_fields,
            annotator_params=annotator_params,
            client=self._client,
            **kwargs
        )

        if follow:
            export.follow()

        return export

    def migrate(self, target, follow=True, **kwargs):
        """
        Migrate the data from the Query to a target dataset.

        Valid optional kwargs include:

        * target_fields
        * include_errors
        * validation_params
        * metadata
        * commit_mode

        """
        from solvebio import DatasetMigration

        # Target can be provided as an object or an ID.
        try:
            target_id = target.id
        except AttributeError:
            target_id = target

        # If a limit is set in the Query and not overridden here, use it.
        limit = kwargs.pop('limit', None)
        if not limit and self._limit < float('inf'):
            limit = self._limit

        # Build the source_params
        params = self._build_query(limit=limit)
        params.pop('offset', None)
        params.pop('ordering', None)

        # target_fields and annotator_params must be passed
        # directly into the migration.
        # Prefer explicitly passed-in values before query values.
        target_fields = kwargs.pop('target_fields', None) or \
            params.pop('target_fields', None)
        annotator_params = kwargs.pop('annotator_params', None) or \
            params.pop('annotator_params', None)

        migration_resp = DatasetMigration.create(
            source_id=self._dataset_id,
            target_id=target_id,
            source_params=params,
            target_fields=target_fields,
            annotator_params=annotator_params,
            client=self._client,
            **kwargs)

        if follow:
            # If migration was created with the parallel flag, then multiple
            # migration objects will be returned.
            if "data" in migration_resp:
                for migration in migration_resp["data"]:
                    migration.follow()
            else:
                migration_resp.follow()

        return migration_resp

    def annotate(self, fields, **kwargs):
        from solvebio.annotate import Annotator

        return Annotator(fields, client=self._client, **kwargs).annotate(self)

    def join(self, query_b, key, key_b=None, prefix="b_", always_prefix=False):
        """Performs a left outer join between the current
        query (query A) and another query (query B).

        Set prefix to None to use a random prefix.
        Enable always_prefix to always apply a prefix.
        """

        # Generate a random ID for the transient query field
        join_id = str(uuid.uuid4())[:8]
        # If prefix is cleared, use the join ID
        if not prefix:
            prefix = join_id + '_'

        # If no key_b is provided, use the same key as for A
        key_b = key_b or key

        # Prepare new returned query object
        new_query = self._clone()

        # Initialize _explode_fields attribute if it does not exist
        new_query._explode_fields = getattr(self, '_explode_fields', None) or []

        # Set list of existing field names to avoid overwriting fields
        # in the join.
        existing_field_names = [f.name for f in self.fields()]
        if new_query._target_fields:
            existing_field_names += [f['name'] for f in new_query._target_fields]
        else:
            new_query._target_fields = []

        # Prepare the filters for the B query expression
        query_params = query_b._build_query()
        base_filter = '["{}", get(record, "{}")]'.format(key_b, key)
        if query_params.get('filters'):
            filters = '[{{"and": [{}, {}]}}]'.format(base_filter, query_params['filters'][0])
        else:
            filters = '[{}]'.format(base_filter)

        # Try to use a unique field for the sub-query data
        query_b_fields = query_b.fields()

        # If a joining key in both datasets is the same and
        # it is not the only one field in a query_b then remove it from query_b
        if key_b == key and not (len(query_b_fields) == 1 and query_b_fields[0].name == key_b):
            query_b_fields = [item for item in query_b_fields if not item.name == key_b]

        query_b_join_field_name = "join_{}".format(join_id)
        target_fields = [
            {
                "name": query_b_join_field_name,
                "data_type": "object",
                "is_list": True,
                "is_transient": True,
                "expression": """
                    dataset_query(
                        "{}",
                        fields={},
                        filters={},
                        entities={},
                        limit={},
                        ordering={}
                    ) if get(record, "{}") else {{}}
                """.format(query_b._dataset_id,
                           [f.name for f in query_b_fields] + [key_b],
                           filters,
                           query_params.get('entities'),
                           query_b._limit if isinstance(query_b._limit, int) else 100000,
                           query_b._ordering,
                           key_b)
            }
        ]

        # Get list of fields to join from query B
        for field in query_b_fields:
            # If "always prefix" is enable, or the field name is found
            # in existing list of names, add the prefix.
            if always_prefix or field.name in existing_field_names:
                name = prefix + field.name
            else:
                name = field.name

            if name in existing_field_names:
                raise Exception("Field '{}' found in both queries, "
                                "please use a different prefix.".format(name))

            # Add a newly created field to list that will be passed to the explode function
            new_query._explode_fields.append(name)

            # Extract all the field values from each joined record
            expression = '[get(item, "{}") for item in get(record, "{}")]'.format(
                field.name, query_b_join_field_name)

            if field.is_list:
                # Handle case where the sub-query contains a list of lists of <field.data_type>,
                # which will happen if the field contains a list of values.
                # In this case, we will flatten it to avoid returning a list of lists.
                expression = '[item for sublist in ' + expression + ' for item in sublist]'

            target_fields.append({
                "name": name,
                "title": field.title,
                "data_type": field.data_type,
                "ordering": field.ordering,
                "is_list": True,
                "is_transient": False,
                "expression": expression,
                "depends_on": [query_b_join_field_name]
            })

        # Add to any existing target fields
        new_query._target_fields += target_fields

        # Preserve existing annotator params (pre_annotation_expression only)
        if not new_query._annotator_params:
            new_query._annotator_params = {}

        new_query._annotator_params['post_annotation_expression'] = \
            "explode(record, fields={})".format(new_query._explode_fields)

        new_query._is_join = True
        return new_query


class BatchQuery(object):
    """
    BatchQuery accepts a list of Query objects and executes them
    in a single request to /v2/batch_query.
    """
    # Allows pre-setting a SolveClient
    _client = None

    def __init__(self, queries, **kwargs):
        """
        Expects a list of Query objects.
        """
        if not isinstance(queries, list):
            queries = [queries]

        self._queries = queries
        self._client = kwargs.get('client') or self._client or client

    def _build_query(self):
        query = {'queries': []}

        for i in self._queries:
            _params = i._build_query(
                dataset=i._dataset_id,
                offset=i._page_offset or 0,
                limit=min(
                    i._page_size,
                    i._limit
                ),
            )
            query['queries'].append(_params)

        return query

    def execute(self, **params):
        _params = self._build_query()
        _params.update(**params)
        response = self._client.post('/v2/batch_query', _params)
        return response


class QueryFile(QueryBase):
    """
    A QueryFile API request wrapper that generates a request for an object content query,
    and can iterate through streaming result sets.
    """
    # The maximum number of results fetched in one go.
    DEFAULT_PAGE_SIZE = 1000

    def __init__(
            self,
            file_id,
            fields=None,
            exclude_fields=None,
            filters=None,
            limit=QueryBase.INF,
            page_size=DEFAULT_PAGE_SIZE,
            result_class=dict,
            debug=False,
            error=None,
            **kwargs):
        """
        Creates a new QueryFile object.

        :Parameters:
          - `file_id`: Unique ID of file to query.
          - `fields` (optional): List of specific fields to retrieve.
          - `exclude_fields` (optional): List of specific fields to exclude.
          - `filters` (optional): Filter or List of filter objects.
          - `result_class` (optional): Class of object returned by query.
          - `limit` (optional): Maximum number of query results to return.
          - `page_size` (optional): Number of results to fetch per query page.
          - `debug` (optional): Sends debug information to the API.
        """
        self._file_id = file_id
        self._data_url = '/v2/objects/{0}/data'.format(file_id)
        self._fields_url = '/v2/objects/{0}/fields'.format(file_id)
        self._result_class = result_class
        self._debug = debug
        self._error = error
        self._fields = fields
        self._exclude_fields = exclude_fields
        self._filters = filters

        if filters:
            if isinstance(filters, Filter):
                filters = [filters]
        else:
            filters = []
        self._filters = filters

        # init response and cursor
        self._response = None
        # Limit defines the total number of results that will be returned
        # from a query involving 1 or more pagination requests.
        self._limit = limit
        # Page offset can only be set by execute(). It is always set to the
        # current absolute offset contained in the buffer.
        self._page_size = int(page_size)
        # Page offset can only be set by execute(). It is always set to the
        # current absolute offset contained in the buffer.
        self._page_offset = None
        # slice is set when the QueryFile is being sliced.
        # In this case, __iter__() and next() will not
        # reset the page_offset to 0 before iterating.
        self._slice = None

        # parameter error checking
        if self._limit < 0:
            raise Exception('\'limit\' parameter must be >= 0')

        # Set up the SolveClient
        # (kwargs overrides pre-set, which overrides global)
        self._client = kwargs.get('client') or self._client or client

    def _clone(self, filters=None, limit=None):
        new = self.__class__(self._file_id,
                             limit=self._limit,
                             fields=self._fields,
                             exclude_fields=self._exclude_fields,
                             page_size=self._page_size,
                             result_class=self._result_class,
                             debug=self._debug,
                             client=self._client)

        new._filters += self._filters

        if filters:
            new._filters += filters

        if limit:
            new._limit = limit

        return new

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

        if self._exclude_fields is not None:
            q['exclude_fields'] = self._exclude_fields

        if self._debug:
            q['debug'] = 'True'

        # Add or modify query parameters
        # (used by BatchQuery and facets)
        q.update(**kwargs)

        return q

    def execute(self, offset=0, **query):
        """
        Executes a query. Additional query parameters can be passed
        as keyword arguments.

        Returns: The request parameters and the raw query response.
        """
        _params = self._build_query(**query)
        self._page_offset = offset

        _params.update(
            offset=self._page_offset,
            limit=min(self._page_size, self._limit)
        )

        logger.debug('executing query. from/limit: %6d/%d' %
                     (_params['offset'], _params['limit']))

        # If the request results in a SolveError (ie bad filter) set the error.
        try:
            self._response = self._client.post(self._data_url, _params)
        except SolveError as e:
            self._error = e
            raise

        logger.debug('query response took: {} ms, total: {}'.
                     format(self._response['took'], self._response['total']))
        return _params, self._response

    def fields(self):
        """Returns all expected fields that will be found in the results."""

        fields = [f for f in self._client.get(self._fields_url, {})['fields']]
        if self._fields:
            fields = [f for f in fields if f in self._fields]
        if self._exclude_fields:
            fields = [f for f in fields if f not in self._exclude_fields]

        return fields
