# -*- coding: utf-8 -*-
import urllib
import re

from ..client import client
from ..query import Query, PagingQuery
from ..help import open_help

from .util import class_to_api_name
from .solveobject import SolveObject, convert_to_solve_object


class APIResource(SolveObject):
    #    from pydbgr.api import debug; debug()
    #    types[self.__class__.__name__] = self

    @classmethod
    def retrieve(cls, id, **params):
        instance = cls(id, **params)
        instance.refresh()
        return instance

    def refresh(self):
        self.refresh_from(self.request('get', self.instance_url()))
        return self

    @classmethod
    def class_name(cls):
        if cls == APIResource:
            raise NotImplementedError(
                'APIResource is an abstract class.  You should perform '
                'actions on its subclasses (e.g. Depository, Dataset)')
        return str(urllib.quote_plus(cls.__name__))

    @classmethod
    def class_url(cls):
        "Returns a versioned URI string for this class"
        # FIXME: DRY with other class_url routines
        return "/v1/{0}".format(class_to_api_name(cls.class_name()))

    def instance_url(self):
        """Get instance URL by ID or full name (if available)"""
        id = self.get('id')
        base = self.class_url()

        if id:
            return '/'.join([base, unicode(id)])
        else:
            raise Exception(
                'Could not determine which URL to request: %s instance '
                'has invalid ID: %r' % (type(self).__name__, id), 'id')


class ListObject(SolveObject):

    def all(self, **params):
        return self.request('get', self['url'], params)

    def create(self, **params):
        return self.request('post', self['url'], params)

    def next_page(self, **params):
        if self['links']['next']:
            return self.request('get', self['links']['next'], params)
        return None

    def prev_page(self, **params):
        if self['links']['prev']:
            self.request('get', self['links']['prev'], params)
        return None

    def objects(self):
        return convert_to_solve_object(self['data'])

    def __iter__(self):
        self._i = 0
        return self

    def next(self):
        if not getattr(self, '_i', None):
            self._i = 0

        if self._i >= len(self['data']):
            # get the next page of results
            next_page = self.next_page()
            if next_page is None:
                raise StopIteration
            self.refresh_from(next_page)
            self._i = 0

        obj = convert_to_solve_object(self['data'][self._i])
        self._i += 1
        return obj


class SingletonAPIResource(APIResource):

    @classmethod
    def retrieve(cls):
        return super(SingletonAPIResource, cls).retrieve(None)

    @classmethod
    def class_url(cls):
        "Returns a versioned URI string for this class"
        # FIXME: DRY with other class_url routines
        return "/v1/{0}".format(class_to_api_name(cls.class_name()))

    def instance_url(self):
        return self.class_url()


class ListableAPIResource(APIResource):

    @classmethod
    def all(cls, **params):
        url = cls.class_url()
        response = client.request('get', url, params)
        return convert_to_solve_object(response)


class SearchableAPIResource(APIResource):

    @classmethod
    def search(cls, query='', **params):
        params.update({'q': query})
        url = cls.class_url()
        response = client.request('get', url, params)
        return convert_to_solve_object(response)


class CreateableAPIResource(APIResource):

    @classmethod
    def create(cls, **params):
        url = cls.class_url()
        response = client.request('post', url, params)
        return convert_to_solve_object(response)


class UpdateableAPIResource(APIResource):

    def save(self):
        self.refresh_from(self.request('patch', self.instance_url(),
                                       self.serialize(self)))
        return self

    def serialize(self, obj):
        params = {}
        if obj._unsaved_values:
            for k in obj._unsaved_values:
                if k == 'id':
                    continue
                params[k] = getattr(obj, k) or ""
        return params


class DeletableAPIResource(APIResource):

    def delete(self, **params):
        self.refresh_from(self.request('delete', self.instance_url(), params))
        return self


# API resources

class User(SingletonAPIResource):
    pass

class Dataset(CreateableAPIResource, ListableAPIResource,
              UpdateableAPIResource):
    ALLOW_FULL_NAME_ID = True
    FULL_NAME_REGEX = r'^([\w\d\-\.]+/){2}[\w\d\-\.]+$'

    @classmethod
    def retrieve(cls, id, **params):
        """Supports lookup by full name"""
        if isinstance(id, unicode) or isinstance(id, str):
            _id = unicode(id).strip()
            id = None
            if re.match(cls.FULL_NAME_REGEX, _id):
                params.update({'full_name': _id})
            else:
                raise Exception('Unrecognized full name.')

        return super(Dataset, cls).retrieve(id, **params)

    def depository_version(self):
        return DepositoryVersion.retrieve(self['depository_version'])

    def depository(self):
        return Depository.retrieve(self['depository'])

    def fields(self, name=None, **params):
        if 'fields_url' not in self:
            raise Exception(
                'Please use Dataset.retrieve({ID}) before doing looking '
                'up fields')

        if name:
            # construct the field's full_name if a field name is provided
            return DatasetField.retrieve(
                '/'.join([self['full_name'], name]))

        response = client.request('get', self.fields_url, params)
        return convert_to_solve_object(response)

    def _data_url(self):
        if 'data_url' not in self:
            if 'id' not in self or not self['id']:
                raise Exception(
                    'No Dataset ID was provided. '
                    'Please instantiate the Dataset '
                    'object with an ID or full_name.')
            # automatically construct the data_url from the ID
            return self.instance_url() + u'/data'
        return self['data_url']

    def query(self, paging=False, **params):
        self._data_url()  # raises an exception if there's no ID
        query_klass = PagingQuery if paging else Query
        q = query_klass(self['id'], **params)
        return q.filter(params.get('filters')) if params.get('filters') else q

    def help(self):
        open_help(self['full_name'])


class DatasetField(CreateableAPIResource, ListableAPIResource,
                   UpdateableAPIResource):
    ALLOW_FULL_NAME_ID = True
    FULL_NAME_REGEX = r'^([\w\d\-\.]+/){3}[\w\d\-\.]+$'

    @classmethod
    def retrieve(cls, id, **params):
        """Supports lookup by ID or full name"""
        if isinstance(id, unicode) or isinstance(id, str):
            _id = unicode(id).strip()
            id = None
            if re.match(cls.FULL_NAME_REGEX, _id):
                params.update({'full_name': _id})
            else:
                raise Exception('Unrecognized full name.')

        return super(DatasetField, cls).retrieve(id, **params)

    def facets(self, **params):
        response = client.request('get', self.facets_url, params)
        return convert_to_solve_object(response)

    def help(self):
        return self.facets()
