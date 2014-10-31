# -*- coding: utf-8 -*-
from ..client import client

from .util import json


def convert_to_solve_object(resp):
    from . import types

    if isinstance(resp, list):
        return [convert_to_solve_object(i) for i in resp]
    elif isinstance(resp, dict) and not isinstance(resp, SolveObject):
        resp = resp.copy()
        klass_name = resp.get('class_name')
        if isinstance(klass_name, basestring):
            klass = types.get(klass_name, SolveObject)
        else:
            klass = SolveObject
        return klass.construct_from(resp)
    else:
        return resp


class SolveObject(dict):
    """Base class for all SolveBio API resource objects"""
    ALLOW_FULL_NAME_ID = False  # Treat full_name parameter as an ID?

    def __init__(self, id=None, **params):
        super(SolveObject, self).__init__()

        # store manually updated values for partial updates
        self._unsaved_values = set()

        if id:
            self['id'] = id
        elif self.ALLOW_FULL_NAME_ID and params.get('full_name'):
            self['full_name'] = params.get('full_name')
            # no ID was provided so temporarily set the id as full_name
            # this will get updated when the resource is refreshed
            self['id'] = params.get('full_name')

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

        for k, v in values.iteritems():
            super(SolveObject, self).__setitem__(
                k, convert_to_solve_object(v))

    def request(self, method, url, params=None):
        response = client.request(method, url, params)
        return convert_to_solve_object(response)

    def __repr__(self):
        if isinstance(self.get('class_name'), basestring):
            ident_parts = [self.get('class_name').encode('utf8')]
        else:
            ident_parts = [type(self).__name__]

        if isinstance(self.get('id'), int):
            ident_parts.append('id=%d' % (self.get('id'),))

        if self.ALLOW_FULL_NAME_ID and \
                isinstance(self.get('full_name'), unicode):
            ident_parts.append('full_name=%s' % (self.get('full_name'),))

        return '<%s at %s> JSON: %s' % (
            ' '.join(ident_parts), hex(id(self)), str(self))

    def __str__(self):
        return json.dumps(self, sort_keys=True, indent=2)

    @property
    def solvebio_id(self):
        return self.id
