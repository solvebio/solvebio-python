"""Solvebio Object API resource"""
import os
import re
import base64
import binascii
import mimetypes

import requests
from requests.packages.urllib3.util.retry import Retry

from solvebio.errors import SolveError
from solvebio.errors import NotFoundError
from solvebio.errors import FileUploadError
from solvebio.utils.md5sum import md5sum

from ..client import client

from .apiresource import CreateableAPIResource
from .apiresource import ListableAPIResource
from .apiresource import SearchableAPIResource
from .apiresource import UpdateableAPIResource
from .apiresource import DeletableAPIResource
from .apiresource import DownloadableAPIResource


class Object(CreateableAPIResource,
             ListableAPIResource,
             DeletableAPIResource,
             SearchableAPIResource,
             UpdateableAPIResource,
             DownloadableAPIResource):
    """
    An object is a resource in a Vault.  It has three possible types,
    though more may be added later: folder, file, and SolveBio Dataset.
    """
    RESOURCE_VERSION = 2

    LIST_FIELDS = (
        ('id', 'ID'),
        ('object_type', 'Type'),
        ('full_path', 'Full Path'),
        ('description', 'Description'),
    )

    # Regex describing an object path.
    PATH_RE = re.compile(r'^[^\/]*(?P<path>(\/[^\/]*)+)$')

    @classmethod
    def validate_full_path(cls, full_path, **kwargs):
        """Helper method to parse a full or partial path and
        return a full path as well as a dict containing path parts.

        Uses the following rules when processing the path:

            * If no domain, uses the current user's account domain
            * If no vault, uses the current user's personal vault.
            * If no path, uses '/' (vault root)

        Returns a tuple containing:

            * The validated full_path
            * A dictionary with the components:
                * domain: the domain of the vault
                * vault: the name of the vault, without domain
                * vault_full_path: domain:vault
                * path: the object path within the vault
                * parent_path: the parent path to the object
                * parent_full_path: the parent full path to the object
                * filename: the object's filename (if any)
                * full_path: the validated full path

        The following components may be overridden using kwargs:

            * vault
            * path

        Object paths (also known as "paths") must begin with a forward slash.

        The following path formats are supported:

            domain:vault:/path -> object "path" in the root of "domain:vault"
            domain:vault/path  -> object "path" in the root of "domain:vault"
            vault:/path        -> object "path" in the root of "vault"
            vault/path         -> object "path" in the root of "vault"
            ~/path             -> object "path" in the root of personal vault
            vault/             -> root of "vault"
            ~/                 -> root of your personal vault

        The following two formats are not supported:

            path               -> invalid/ambiguous path (exception)
            vault:path         -> invalid/ambiguous path (exception)
            vault:path/path    -> unsupported, interpreted as domain:vault/path

        """
        from solvebio.resource.vault import Vault

        _client = kwargs.pop('client', None) or cls._client or client

        if not full_path:
            raise Exception(
                'Invalid path: ',
                'Full path must be in one of the following formats: '
                '"vault:/path", "domain:vault:/path", or "~/path"')

        # Parse the vault's full_path, using overrides if any
        input_vault = kwargs.get('vault') or full_path
        try:
            vault_full_path, path_dict = \
                Vault.validate_full_path(input_vault, client=_client)
        except Exception as err:
            raise Exception('Could not determine vault from "{0}": {1}'
                            .format(input_vault, err))

        if kwargs.get('path'):
            # Allow override of the object_path.
            full_path = '{0}:/{1}'.format(vault_full_path, kwargs['path'])

        match = cls.PATH_RE.match(full_path)
        if match:
            object_path = match.groupdict()['path']
        else:
            raise Exception(
                'Cannot find a valid object path in "{0}". '
                'Full path must be in one of the following formats: '
                '"vault:/path", "domain:vault:/path", or "~/path"'
                .format(full_path))

        # Remove double slashes
        object_path = re.sub('//+', '/', object_path)
        if object_path != '/':
            # Remove trailing slash
            object_path = object_path.rstrip('/')

        path_dict['path'] = object_path
        path_dict['full_path'] = '{domain}:{vault}:{path}'.format(**path_dict)

        # Assumes no trailing slash, will be '' if is a vault root
        path_dict['filename'] = os.path.basename(object_path)

        # Will be / if parent is vault root
        path_dict['parent_path'] = os.path.dirname(object_path)
        path_dict['parent_full_path'] = '{vault_full_path}:{parent_path}' \
            .format(**path_dict)

        return path_dict['full_path'], path_dict

    @classmethod
    def get_by_full_path(cls, full_path, **params):
        # Don't pop client from params since **params is used below
        _client = params.get('client', None) or cls._client or client
        full_path, _ = cls.validate_full_path(full_path, client=_client)
        assert_type = params.pop('assert_type', None)
        params.update({'full_path': full_path})
        obj = cls._retrieve_helper('object', 'full_path', full_path,
                                   **params)
        if obj and assert_type and obj['object_type'] != assert_type:
            raise SolveError(
                "Expected a {} but found a {} at {}"
                .format(assert_type, obj['object_type'], full_path))

        return obj

    @classmethod
    def get_by_path(cls, path, **params):
        assert_type = params.pop('assert_type', None)
        params.update({'path': path})
        obj = cls._retrieve_helper('object', 'path', path, **params)
        if obj and assert_type and obj['object_type'] != assert_type:
            raise SolveError(
                "Expected a {} but found a {} at {}"
                .format(assert_type, obj['object_type'], path))

        return obj

    @classmethod
    def upload_file(cls, local_path, remote_path, vault_full_path, **kwargs):
        from solvebio import Vault
        from solvebio import Object

        _client = kwargs.pop('client', None) or cls._client or client

        local_path = os.path.expanduser(local_path)
        if os.stat(local_path).st_size == 0:
            print('Notice: Cannot upload empty file {0}'.format(local_path))
            return

        # Get vault
        vault = Vault.get_by_full_path(vault_full_path, client=_client)

        # Get MD5, mimetype, and file size for the object
        local_md5, _ = md5sum(local_path, multipart_threshold=None)
        _, mimetype = mimetypes.guess_type(local_path)
        size = os.path.getsize(local_path)

        # Check if object exists already and compare md5sums
        full_path, path_dict = Object.validate_full_path(
            os.path.join('{}:{}'.format(vault.full_path, remote_path),
                         os.path.basename(local_path)))
        try:
            obj = cls.get_by_full_path(full_path)
            if not obj.is_file:
                print('WARNING: A {} currently exists at {}'
                      .format(obj.object_type, full_path))
            else:
                # Check against md5sum of remote file
                if obj.md5 == local_md5:
                    print('WARNING: File {} (md5sum {}) already exists, '
                          'not uploading'.format(full_path, local_md5))
                    return obj
                else:
                    print('WARNING: File {} exists on SolveBio with different '
                          'md5sum (local: {} vs remote: {}) Uploading anyway, '
                          'but not overwriting.'
                          .format(full_path, local_md5, obj.md5))
        except NotFoundError:
            pass

        # Lookup parent object
        if path_dict['parent_path'] == '/':
            parent_object_id = None
        else:
            parent_obj = Object.get_by_full_path(
                path_dict['parent_full_path'], assert_type='folder',
                client=_client
            )
            parent_object_id = parent_obj.id

        description = kwargs.get('description')

        # Create the file, and upload it to the Upload URL
        obj = Object.create(
            vault_id=vault.id,
            parent_object_id=parent_object_id,
            object_type='file',
            filename=os.path.basename(local_path),
            md5=local_md5,
            mimetype=mimetype,
            size=size,
            description=description,
            tags=kwargs.get('tags', []) or [],
            client=_client
        )

        print('Notice: File created for {0} at {1}'.format(local_path,
                                                           obj.path))
        print('Notice: Upload initialized')

        upload_url = obj.upload_url

        headers = {
            'Content-MD5': base64.b64encode(binascii.unhexlify(local_md5)),
            'Content-Type': mimetype,
            'Content-Length': str(size),
        }

        # Use a session with a retry policy to handle connection errors.
        session = requests.Session()
        max_retries = 5
        retry = Retry(
            total=max_retries,
            read=max_retries,
            connect=max_retries,
            backoff_factor=0.3,
            status_forcelist=(500, 502, 504, 400),
        )
        session.mount(
            'https://', requests.adapters.HTTPAdapter(max_retries=retry))
        upload_resp = session.put(upload_url,
                                  data=open(local_path, 'rb'),
                                  headers=headers)

        if upload_resp.status_code != 200:
            print('WARNING: Upload status code for {0} was {1}'.format(
                local_path, upload_resp.status_code
            ))
            # Clean up the failed upload
            obj.delete(force=True)
            raise FileUploadError(upload_resp.content)
        else:
            print('Notice: Successfully uploaded {0} to {1}'.format(local_path,
                                                                    obj.path))

        return obj

    def _object_list_helper(self, **params):
        """Helper method to get objects within"""

        if not self.is_folder:
            raise SolveError(
                "Only folders contain child objects. This is a {}"
                .format(self.object_type))

        params['vault_id'] = self.vault_id
        if 'recursive' in params:
            params['ancestor_id'] = self.id
            params['limit'] = 1000
        else:
            params['parent_object_id'] = self.id

        items = self.all(client=self._client, **params)
        return items

    def files(self, **params):
        return self._object_list_helper(object_type='file', **params)

    def folders(self, **params):
        return self._object_list_helper(object_type='folder', **params)

    def datasets(self, **params):
        return self._object_list_helper(object_type='dataset', **params)

    def objects(self, **params):
        return self._object_list_helper(**params)

    def ls(self, **params):
        return self.objects(**params)

    def query(self, query=None, **params):
        """Shortcut to query the underlying Dataset object"""
        from solvebio import Dataset

        if not self.is_dataset:
            raise SolveError(
                "The query method can only be used by a dataset. Found a {}"
                .format(self.object_type))

        return Dataset(self.dataset_id).query(query=query, **params)

    @property
    def parent(self):
        """ Returns the parent object """
        if self['parent_object_id']:
            return self.retrieve(self['parent_object_id'], client=self._client)

        return None

    @property
    def vault(self):
        """ Returns the vault object """
        from . import Vault
        return Vault.retrieve(self['vault_id'], client=self._client)

    @property
    def is_dataset(self):
        return self.object_type == 'dataset'

    @property
    def is_folder(self):
        return self.object_type == 'folder'

    @property
    def is_file(self):
        return self.object_type == 'file'

    def tag(self, tags, remove=False, dry_run=False, apply_save=False):
        """Add or remove tags on an object"""

        def lowercase(x):
            return x.lower()

        existing_tags = map(lowercase, self.tags)

        if remove:
            removal_tags = [tag for tag in tags
                            if lowercase(tag) in existing_tags]
            if removal_tags:
                print('{}Notice: Removing tags: {} from object: {}'
                      .format('[Dry Run] ' if dry_run else '',
                              ', '.join(removal_tags), self.full_path))

                updated_tags = [tag for tag in existing_tags
                                if tag not in removal_tags]
            else:
                print('{}Notice: Object {} does not contain any of the '
                      'following tags: {}'.format(
                          '[Dry Run] ' if dry_run else '',
                          self.full_path, ', '.join(tags)))
                return False
        else:
            new_tags = [tag for tag in tags
                        if lowercase(tag) not in existing_tags]
            if new_tags:
                print('{}Notice: Adding tags: {} to object: {}'
                      .format('[Dry Run] ' if dry_run else '',
                              ', '.join(new_tags), self.full_path))
                updated_tags = self.tags + new_tags
            else:
                print('{}Notice: Object {} already contains these tags: {}'
                      .format('[Dry Run] ' if dry_run else '',
                              self.full_path, ', '.join(tags)))
                return False

        if not dry_run and apply_save:
            self.tags = updated_tags
            self.save()

        return True
