# -*- coding: utf-8 -*-
"""
Abstract classes from which specific API resources (Depository,
Annotation, ... ) inheret
"""
import os
import requests
import tempfile
import urllib

from ..client import client, _handle_api_error, _handle_request_error
from .. import SolveError

from .util import class_to_api_name
from .solveobject import SolveObject, convert_to_solve_object


def conjure_file(url, path):
    """Make up a file name based on info in *url* and *path*.

    :param url: str url to base filename
    :param path: str can be a full path, a directory name, or None.
                 If path is *None*, we'll use
                 use the current directory plus any name we find in url.
                 If path is a directory well use that plus the name found in url.
                 If it a non-directory string, we'll ignore any filename found in
                 *url* and use that.
    :returns: str a full path name
    """
    values = url.split('%3B%20filename%3D')
    if len(values) != 2:
        short_name = tempfile.mkstemp(suffix='gz')
    else:
        short_name = values[1]
    if path:
        if os.path.isdir(path):
            path = os.path.join(path, short_name)
    else:
        path = short_name
    return path


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
                'actions on its subclasses (e.g. Depository, Dataset)')
        return str(urllib.quote_plus(cls.__name__))

    @classmethod
    def class_url(cls):
        """Returns a versioned URI string for this class"""
        return "/v1/{0}".format(class_to_api_name(cls.class_name()))

    def instance_url(self):
        'Get instance URL by ID or full name (if available)'
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
        """Lists all items in a class that you have access to"""
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
        """Returns a versioned URI string for this class"""
        return "/v1/{0}".format(class_to_api_name(cls.class_name()))

    def instance_url(self):
        return self.class_url()


class CreateableAPIResource(APIResource):

    @classmethod
    def create(cls, **params):
        url = cls.class_url()
        response = client.request('post', url, params)
        return convert_to_solve_object(response)


class DeletableAPIResource(APIResource):

    def delete(self, **params):
        self.refresh_from(self.request('delete', self.instance_url(), params))
        return self


class DownloadableAPIResource(APIResource):

    @classmethod
    def delete(cls, id):
        """Delete the sample with the id. The id is that returned by a
        create, or found by listing all samples."""

        try:
            response = client.request('delete', cls(id).instance_url())
        except SolveError as response:
            pass
        return convert_to_solve_object(response)

    @classmethod
    def download(cls, id, path=None):
        """Download the sample with the id. The id is that returned by a
        create, or found by listing all samples."""

        download_url = cls(id).instance_url() + '/download'
        response = client.request('get', download_url, allow_redirects=False)
        if 302 != response.status_code:
            # Some kind of error. We expect a redirect
            return None
        download_url = response.headers['location']
        download_path = conjure_file(download_url, path)

        try:
            response = requests.request(method='get', url=download_url)
        except Exception as e:
            _handle_request_error(e)

        if not (200 <= response.status_code < 400):
            _handle_api_error(response)

        with open(download_path, 'wb') as fileobj:
            fileobj.write(response._content)

        response = convert_to_solve_object(response)
        response.filename = download_path
        return response


class ListableAPIResource(APIResource):
    """Has one method: *all()* which lists everything in the resource."""

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


class UploadableAPIResource(APIResource):
    """Defines *create()*, *create_from_file()* and
    *create_from_url()* methods which allow one to upload a (VCF) file
    to be stored on the system.
    """

    @classmethod
    def create(cls, genome_build, **params):
        if 'vcf_url' in params:
            if 'vcf_file' in params:
                raise TypeError('Specified both vcf_url and vcf_file; ' +
                                'use only one')
            return cls.create_from_url(genome_build, params['vcf_url'])
        elif 'vcf_file' in params:
            return cls.create_from_file(genome_build, params['vcf_file'])
        else:
            raise TypeError('Must specify exactly one of vcf_url or ' +
                            'vcf_file parameter')

    @classmethod
    def create_from_file(cls, genome_build, vcf_file):
        """Creates a from the specified file.  The data of
        the should be in VCF format."""

        files = {'vcf_file': open(vcf_file, 'rb')}
        params = {'genome_build': genome_build}
        response = client.request('post', cls.class_url(), params=params,
                                  files=files)
        return convert_to_solve_object(response)

    @classmethod
    def create_from_url(cls, genome_build, vcf_url):
        """Creates a from the specified URL.  The data of
        the should be in VCF format."""

        params = {'genome_build': genome_build,
                  'vcf_url': vcf_url}
        try:
            response = client.request('post', cls.class_url(), params=params)
        except SolveError as response:
            pass
        return convert_to_solve_object(response)
