# -*- coding: utf-8 -*-
import urllib
import re

# from utils.tabulate import tabulate
from .client import client
from .query import Query
from .help import open_help

try:
    import json
except ImportError:
    json = None

# test for compatible json module
if not (json and hasattr(json, 'loads')):
    import simplejson as json


def camelcase_to_underscore(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def convert_to_solve_object(resp):
    types = {
        'Depository': Depository,
        'DepositoryVersion': DepositoryVersion,
        'Dataset': Dataset,
        'DatasetField': DatasetField,
        'User': User,
        'list': ListObject
    }

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

    def __init__(self, id=None, **params):
        super(SolveObject, self).__init__()

        if id:
            self['id'] = id
        elif params.get('full_name'):
            self['full_name'] = params.get('full_name')

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
        except KeyError, err:
            raise AttributeError(*err.args)

    @classmethod
    def construct_from(cls, values):
        """Used to create a new object from an HTTP response"""
        instance = cls(values.get('id'))
        instance.refresh_from(values)
        return instance

    def refresh_from(self, values):
        self.clear()
        for k, v in values.iteritems():
            super(SolveObject, self).__setitem__(
                k, convert_to_solve_object(v))

    def request(self, method, url, params=None):
        response = client.request(method, url, params)
        return convert_to_solve_object(response)

    def __repr__(self):
        ident_parts = [type(self).__name__]

        if isinstance(self.get('class_name'), basestring):
            ident_parts.append(self.get('class_name').encode('utf8'))

        if isinstance(self.get('id'), int):
            ident_parts.append('id=%d' % (self.get('id'),))

        if isinstance(self.get('full_name'), unicode):
            ident_parts.append('full_name=%s' % (self.get('full_name'),))

        return '<%s at %s> JSON: %s' % (
            ' '.join(ident_parts), hex(id(self)), str(self))

    def __str__(self):
        return json.dumps(self, sort_keys=True, indent=2)

    @property
    def solvebio_id(self):
        return self.id or self.full_name


class APIResource(SolveObject):

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
        cls_name = cls.class_name()
        # pluralize
        if cls_name.endswith('y'):
            cls_name = cls_name[:-1] + 'ie'
        cls_name = camelcase_to_underscore(cls_name)
        return "/v1/%ss" % (cls_name,)

    def instance_url(self):
        """Get instance URL by ID or full name (if available)"""
        id = self.get('id')
        full_name = self.get('full_name')
        base = self.class_url()

        if id:
            return "%s/%d" % (base, id)
        elif full_name:
            return "%s/%s" % (base, full_name)
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
        cls_name = cls.class_name()
        cls_name = camelcase_to_underscore(cls_name)
        return "/v1/%s" % (cls_name,)

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


class User(SingletonAPIResource):
    pass


class Depository(CreateableAPIResource, ListableAPIResource,
                 SearchableAPIResource):
    FULL_NAME_REGEX = r'^[\w\d\-\.]+$'

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

        return super(Depository, cls).retrieve(id, **params)

    def versions(self, name=None, **params):
        if name:
            # construct the depo version full name
            return DepositoryVersion.retrieve(
                '/'.join([self['full_name'], name]))

        response = client.request('get', self.versions_url, params)
        return convert_to_solve_object(response)

    def help(self):
        open_help(self['full_name'])


class DepositoryVersion(CreateableAPIResource, ListableAPIResource):
    FULL_NAME_REGEX = r'^[\w\d\-\.]+/[\w\d\-\.]+$'

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

        return super(DepositoryVersion, cls).retrieve(id, **params)

    def datasets(self, name=None, **params):
        if name:
            # construct the dataset full name
            return Dataset.retrieve(
                '/'.join([self['full_name'], name]))

        response = client.request('get', self.datasets_url, params)
        return convert_to_solve_object(response)

    def help(self):
        open_help(self['full_name'])


class Dataset(CreateableAPIResource, ListableAPIResource):
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
        if name:
            # construct the field URN
            return DatasetField.retrieve(
                '/'.join([self['full_name'], name]))

        response = client.request('get', self.fields_url, params)
        return convert_to_solve_object(response)

    def query(self, **params):
        q = Query(self['data_url'], **params)
        if params.get('filters'):
            return q.filter(params.get('filters'))
        return q

    def help(self):
        open_help(self['full_name'])


class DatasetField(CreateableAPIResource, ListableAPIResource):
    FULL_NAME_REGEX = r'^([\w\d\-\.]+/){3}[\w\d\-\.]+$'

    @classmethod
    def retrieve(cls, id, **params):
        """Supports lookup by URN or full name"""
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
