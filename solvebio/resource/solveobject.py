# -*- coding: utf-8 -*-
from __future__ import absolute_import
import six

import sys

from ..client import client
from .util import json


def convert_to_solve_object(resp):
    from . import types

    if isinstance(resp, list):
        return [convert_to_solve_object(i) for i in resp]
    elif isinstance(resp, dict) and not isinstance(resp, SolveObject):
        resp = resp.copy()
        klass_name = resp.get('class_name')
        if isinstance(klass_name, six.string_types):
            klass = types.get(klass_name, SolveObject)
        else:
            klass = SolveObject
        return klass.construct_from(resp)
    else:
        return resp


class SolveObject(dict):
    """Base class for all SolveBio API resource objects"""

    def __init__(self, id=None, **params):
        super(SolveObject, self).__init__()

        # store manually updated values for partial updates
        self._unsaved_values = set()

        if id:
            self['id'] = id

    def __setattr__(self, k, v):
        if k[0] == '_' or k in self.__dict__:
            return super(SolveObject, self).__setattr__(k, v)
        else:
            self[k] = v

    def __getattr__(self, k):
        if k[0] == '_':
            raise AttributeError(k)

        try:
            return self[k]
        except KeyError as err:
            raise AttributeError(*err.args)

    def __setitem__(self, k, v):
        super(SolveObject, self).__setitem__(k, v)
        self._unsaved_values.add(k)

    @classmethod
    def construct_from(cls, values):
        """Used to create a new object from an HTTP response"""
        instance = cls(values.get('id'))
        instance.refresh_from(values)
        return instance

    def refresh_from(self, values):
        self.clear()
        self._unsaved_values = set()

        for k, v in six.iteritems(values):
            super(SolveObject, self).__setitem__(
                k, convert_to_solve_object(v))

    def request(self, method, url, **kwargs):
        response = client.request(method, url, **kwargs)
        return convert_to_solve_object(response)

    def __repr__(self):
        if isinstance(self.get('class_name'), six.string_types):
            ident_parts = [self.get('class_name')]
        else:
            ident_parts = [type(self).__name__]

        if isinstance(self.get('id'), int):
            ident_parts.append('id=%d' % (self.get('id'),))

        if isinstance(self.get('full_name'), six.text_type):
            ident_parts.append(
                'full_name=%s' % (self.get('full_name'),))

        _repr = '<%s at %s> JSON: %s' % (
            ' '.join(ident_parts), hex(id(self)), str(self))

        if sys.version_info[0] < 3:
            return _repr.encode('utf-8')

        return _repr

    def __str__(self):
        return json.dumps(self, sort_keys=True, indent=2)

    @property
    def solvebio_id(self):
        return self.id
