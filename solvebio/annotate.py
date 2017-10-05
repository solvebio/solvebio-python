# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .client import client

import logging
logger = logging.getLogger('solvebio')


class Annotator(object):
    """
    Runs the synchronous annotate endpoint against
    batches of results from a query.
    """
    CHUNK_SIZE = 100

    # Allows pre-setting a SolveClient
    _client = None

    def __init__(self, fields, include_errors=False, **kwargs):
        self.buffer = []
        self.fields = fields
        self.include_errors = include_errors
        self._client = kwargs.get('client') or self._client or client

    def annotate(self, records, chunk_size=CHUNK_SIZE):
        """Annotate a set of records with stored fields.

        Args:
            records: A list or iterator (can be a Query object)
            chunk_size: The number of records to annotate at once (max 500).

        Returns:
            A generator that yields one annotated record at a time.
        """
        chunk = []
        for i, record in enumerate(records):
            chunk.append(record)
            if (i + 1) % chunk_size == 0:
                for r in self._execute(chunk):
                    yield r
                chunk = []

        if chunk:
            for r in self._execute(chunk):
                yield r
            chunk = []

    def _execute(self, chunk):
        data = {
            'records': chunk,
            'fields': self.fields,
            'include_errors': self.include_errors
        }

        for r in self._client.post('/v1/annotate', data)['results']:
            yield r


class Expression(object):
    """Runs a single SolveBio expression."""

    # Allows pre-setting a SolveClient
    _client = None

    def __init__(self, expr, **kwargs):
        self.expr = expr
        self._client = kwargs.get('client') or self._client or client

    def evaluate(self, data=None, data_type='string', is_list=False):
        """Evaluates the expression with the provided context and format."""
        payload = {
            'data': data,
            'expression': self.expr,
            'data_type': data_type,
            'is_list': is_list
        }
        res = self._client.post('/v1/evaluate', payload)
        return res['result']

    def __repr__(self):
        return '<Expression "{0}">'.format(self.expr)
