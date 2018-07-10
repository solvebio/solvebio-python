# -*- coding: utf-8 -*-
from __future__ import absolute_import
import six
from six.moves import zip
from six.moves.urllib.parse import unquote
from six.moves import input as raw_input

import os
import requests
import tempfile

try:
    from urllib import quote_plus
except ImportError:
    from urllib.parse import quote_plus

from ..client import client, _handle_api_error, _handle_request_error
from ..utils.tabulate import tabulate
from ..utils.printing import pager
# from solvebio.errors import NotFoundError
from ..errors import NotFoundError

from .util import class_to_api_name
from .solveobject import SolveObject, convert_to_solve_object


class APIResource(SolveObject):
    """Abstract Class for an API Resource"""

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
                'actions on its subclasses (e.g. Vault, Object, Dataset)')
        return str(quote_plus(cls.__name__))

    @classmethod
    def class_url(cls):
        """Returns a versioned URI string for this class"""
        base = 'v{0}'.format(getattr(cls, 'RESOURCE_VERSION', '1'))
        return "/{0}/{1}".format(base, class_to_api_name(cls.class_name()))

    def instance_url(self):
        """Get instance URL by ID"""
        id_ = self.get(self.ID_ATTR)
        base = self.class_url()

        if id_:
            return '/'.join([base, six.text_type(id_)])
        else:
            raise Exception(
                'Could not determine which URL to request: %s instance '
                'has invalid ID: %r' % (type(self).__name__, id_),
                self.ID_ATTR)


class ListObject(SolveObject):

    def all(self, **params):
        """Lists all items in a class that you have access to"""
        return self.request('get', self['url'], params=params)

    def create(self, **params):
        return self.request('post', self['url'], data=params)

    def first_page(self, **params):
        url = getattr(self, '_first_page_url', self['url'])
        return self.request('get', url, params=params)

    def next_page(self, **params):
        if self['links']['next']:
            return self.request('get', self['links']['next'], params=params)
        return None

    def prev_page(self, **params):
        if self['links']['prev']:
            return self.request('get', self['links']['prev'], params=params)
        return None

    def solve_objects(self):
        return convert_to_solve_object(self['data'], client=self._client)

    def set_tabulate(self, fields, **kwargs):
        self._tabulate = lambda data:\
            tabulate([[d[i] for i in fields] for d in data], **kwargs)

    def __len__(self):
        return self['total']

    def __str__(self):
        if getattr(self, '_tabulate', None):
            return '\n' + self._tabulate(self['data'])
        return super(ListObject, self).__str__()

    def __iter__(self):
        self._i = 0

        # Store the URL of the first page if we haven't yet.
        self._first_page_url = getattr(self, '_first_page_url', self['url'])
        if self._first_page_url != self['url']:
            self.refresh_from(self.first_page())

        return self

    def __next__(self):
        """Python 3"""
        return self.next()

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

        obj = convert_to_solve_object(self['data'][self._i],
                                      client=self._client)
        self._i += 1
        return obj


class SingletonAPIResource(APIResource):

    @classmethod
    def retrieve(cls, **kwargs):
        _client = kwargs.pop('client', None) or cls._client or client
        return super(SingletonAPIResource, cls).retrieve(None, client=_client)

    @classmethod
    def class_url(cls):
        """
        Returns a versioned URI string for this class,
        and don't pluralize the class name.
        """
        base = 'v{0}'.format(getattr(cls, 'RESOURCE_VERSION', '1'))
        return "/{0}/{1}".format(base, class_to_api_name(
            cls.class_name(), pluralize=False))

    def instance_url(self):
        return self.class_url()


class CreateableAPIResource(APIResource):

    @classmethod
    def create(cls, **params):
        _client = params.pop('client', None) or cls._client or client
        url = cls.class_url()
        response = _client.post(url, data=params)
        return convert_to_solve_object(response, client=_client)


class DeletableAPIResource(APIResource):

    def delete(self, **params):
        printable_name = class_to_api_name(
            self.class_name(), pluralize=False).replace('_', ' ')
        if not params.pop('force', False):
            res = raw_input('Are you sure you want to delete this %s? '
                            '[y/N] ' % printable_name)
            if res.strip().lower() != 'y':
                print('Not performing deletion.')
                return

        response = self.request('delete', self.instance_url(), params=params)
        return convert_to_solve_object(response, client=self._client)


class DownloadableAPIResource(APIResource):

    def download(self, path=None, **kwargs):
        """
        Download the file to the specified directory or file path.
        Downloads to a temporary directory if no path is specified.

        Returns the absolute path to the file.
        """
        download_url = self.download_url(**kwargs)
        try:
            # For vault objects, use the object's filename
            # as the fallback if none is specified.
            filename = self.filename
        except AttributeError:
            # If the object has no filename attribute,
            # extract one from the download URL.
            filename = download_url.split('%3B%20filename%3D')[1]
            # Remove additional URL params from the name and "unquote" it.
            filename = unquote(filename.split('&')[0])

        if path:
            path = os.path.expanduser(path)
            # If the path is a dir, use the extracted filename
            if os.path.isdir(path):
                path = os.path.join(path, filename)
        else:
            # Create a temporary directory for the file
            path = os.path.join(tempfile.gettempdir(), filename)

        try:
            response = requests.request(method='get', url=download_url)
        except Exception as e:
            _handle_request_error(e)

        if not (200 <= response.status_code < 400):
            _handle_api_error(response)

        with open(path, 'wb') as fileobj:
            fileobj.write(response._content)

        return path

    def download_url(self, **kwargs):
        download_url = self.instance_url() + '/download'
        # Don't redirect, just return the signed S3 URL
        kwargs.update({'redirect': ''})
        response = self.request(
            'get', download_url, params=kwargs, allow_redirects=False)

        return response.get('url') or response.get('download_url')


class ListableAPIResource(APIResource):
    """Has one method: *all()* which lists everything in the resource."""

    @classmethod
    def all(cls, **params):
        _client = params.pop('client', None) or cls._client or client
        url = cls.class_url()
        response = _client.get(url, params)
        results = convert_to_solve_object(response, client=_client)

        # If the object has LIST_FIELDS, setup tabulate
        if len(results.data) > 0:
            list_fields = getattr(results.data[0], 'LIST_FIELDS', None)
            if list_fields:
                fields, headers = list(zip(*list_fields))
                results.set_tabulate(fields, headers=headers, sort=False)

        return results

    @classmethod
    def _retrieve_helper(cls, model_name, field_name, error_value, **params):
        _client = params.pop('client', None) or cls._client or client
        url = cls.class_url()
        response = _client.get(url, params)
        results = convert_to_solve_object(response, client=_client)
        objects = results.data
        allow_multiple = params.pop('allow_multiple', None)
        if len(objects) > 1:
            if allow_multiple:
                return objects
            else:
                raise Exception('Multiple {0}s found with {1} "{2}"'
                                .format(model_name, field_name, error_value))
        elif len(objects) == 1:
            return objects[0]
        else:
            raise NotFoundError('No {0} found with {1} "{2}"'
                                .format(model_name, field_name, error_value))

    @classmethod
    def pager(cls, **params):
        return pager(cls.all, **params)

    def __repr__(self):
        return tabulate(list(self.items()), ['Fields', 'Data'],
                        aligns=['right', 'left'], sort=True)


class SearchableAPIResource(APIResource):

    @classmethod
    def search(cls, query='', **params):
        _client = params.pop('client', None) or cls._client or client
        params.update({'q': query})
        url = cls.class_url()
        response = _client.get(url, params)
        results = convert_to_solve_object(response, client=_client)

        # If the object has LIST_FIELDS, setup tabulate
        if len(results.data) > 0:
            list_fields = getattr(results.data[0], 'LIST_FIELDS', None)
            if list_fields:
                fields, headers = list(zip(*list_fields))
                results.set_tabulate(fields, headers=headers)

        return results


class UpdateableAPIResource(APIResource):

    def save(self):
        self.refresh_from(self.request('patch', self.instance_url(),
                                       data=self.serialize(self)))
        return self

    def serialize(self, obj):
        params = {}
        if obj._unsaved_values:
            for k in obj._unsaved_values:
                if k == 'id' or k == self.ID_ATTR:
                    continue
                params[k] = getattr(obj, k) or ""
        return params
