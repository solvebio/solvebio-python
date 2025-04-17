# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .client import client
from .resource import Object
from .resource import Vault
from .query import QueryBase
from .query import Query
from .query import Filter

import logging
logger = logging.getLogger('solvebio')


class GlobalSearch(Query):
    """
    GlobalSearch acts as a request wrapper that generates a request from Filter objects,
    and can iterate through streaming result sets.
    """

    def __init__(
            self,
            query=None,
            filters=None,
            entities=None,
            entities_match='any',
            vault_scope='all',
            ordering=None,
            limit=float('inf'),
            page_size=QueryBase.DEFAULT_PAGE_SIZE,
            result_class=dict,
            debug=False,
            raw_results=False,
            **kwargs):
        """
        Creates a new Query object.

        :Parameters:
          - `query` (optional): An optional query string (advanced search).
          - `filters` (optional): Filter or List of filter objects.
          - `entities` (optional): List of entity tuples to filter on (entity type, entity).
          - `entities_match` (optional): Can be 'all' or 'any' (match any provided entity).
          - `vault_scope` (optional): Can be 'all' or 'access'.
          - `ordering` (optional): List of fields to order the results by.
          - `limit` (optional): Maximum number of query results to return.
          - `page_size` (optional): Number of results to fetch per query page.
          - `result_class` (optional): Class of object returned by query.
          - `debug` (optional): Sends debug information to the API.
          - `raw_results` (optional): Whether to use raw API response or to cast logical
             objects to Vault and Object instances.
        """
        super(GlobalSearch, self).__init__(None)
        self._data_url = '/v2/search'
        self._query = query
        self._entities = entities
        self._entities_match = entities_match
        self._vault_scope = vault_scope
        self._ordering = ordering
        self._result_class = result_class
        self._debug = debug
        self._raw_results = raw_results
        self._error = None

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

        if not 0 < self._page_size <= self.MAX_PAGE_SIZE:
            raise Exception('\'page_size\' parameter must be in '
                            'range [1, {}]'.format(self.MAX_PAGE_SIZE))

        # Set up the SolveClient
        # (kwargs overrides pre-set, which overrides global)
        self._client = kwargs.get('client') or self._client or client

    def _clone(self, filters=None, entities=None, limit=None):
        new = self.__class__(query=self._query,
                             limit=self._limit,
                             entities=self._entities,
                             ordering=self._ordering,
                             page_size=self._page_size,
                             result_class=self._result_class,
                             vault_scope=self._vault_scope,
                             entities_match=self._entities_match,
                             debug=self._debug,
                             client=self._client)
        new._filters += self._filters

        if entities:
            new._entities = entities

        if filters:
            new._filters += filters

        if limit is not None:
            new._limit = limit

        return new

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
        return super(GlobalSearch, self).__len__()

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

        if self._entities is not None:
            q['entities'] = self._entities

        if self._ordering is not None:
            q['ordering'] = self._ordering

        if self._vault_scope is not None:
            q['vault_scope'] = self._vault_scope

        if self._entities_match is not None:
            q['entities_match'] = self._entities_match

        if self._debug:
            q['debug'] = 'True'

        # Add or modify query parameters
        # (used by BatchQuery and facets)
        q.update(**kwargs)

        return q

    def execute(self, offset=0, **query):
        def _process_result(result):
            # Internally the client uses object_type, not type
            result['object_type'] = result['type']
            if result['object_type'] == 'vault':
                return Vault.construct_from(result)
            else:
                return Object.construct_from(result)

        # Call superclass method execute
        super(GlobalSearch, self).execute(offset, **query)

        # Cast logical objects from response to Object/Vault instances
        if not self._raw_results:
            self._response['results'] = [_process_result(i) for i in self._response['results']]

    def entity(self, **kwargs):
        """
        Returns GlobalSearch instance with the query args combined with
        existing set with AND.

        kwargs can contain only one entity, entity_type as parameter name and entity as its value.
        If entity is already set for the GlobalSearch, it will be overridden.
        """

        if not kwargs:
            raise AttributeError('Faceting requires at least one field')

        return self._clone(entities=list(kwargs.items()))

    def subjects(self):
        """Returns the list of subjects"""

        # Executes a query to get a full API response which contains subjects list
        gs = self.limit(0)
        gs.execute(include_subjects=True, include_all_subjects=True)

        return gs._response.get('subjects')

    def subjects_count(self):
        """Returns the number of subjects"""

        # Executes a query to get a full API response which contains subjects list
        gs = self.limit(0)
        gs.execute()

        return gs._response.get('subjects_count')

    def vaults(self):
        """Returns the list of vaults"""

        # Executes a query to get a full API response which contains vaults list
        gs = self.limit(0)
        gs.execute(include_vaults=True)

        return gs._response.get('vaults')
