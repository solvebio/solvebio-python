"""Solvebio Object API resource"""
import os
import re
import base64
import binascii
import mimetypes

import requests

from solvebio import SolveError
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
        ('vault_id', 'Vault ID'),
        ('vault_name', 'Vault Name'),
        ('object_type', 'Object Type'),
        ('path', 'Path'),
        ('filename', 'Filename'),
        ('description', 'Description'),
    )

    @classmethod
    def validate_path(cls, path, **kwargs):
        """ Helper method to return a full path

            If no account_domain, assumes user's account domain
            If no vault, uses personal vault.
            If no path, uses /
        """
        _client = kwargs.pop('client', None) or cls._client or client

        # Remove double slashes and leading ':'
        path = re.sub('//+', '/', path.lstrip(':'))

        parts = path.split(':', 2)
        if len(parts) == 3:
            account_domain, vault_name, object_path = parts
        elif len(parts) == 2:
            # if no slash assume user means root
            if '/' not in parts[1]:
                account_domain, vault_name = parts
                object_path = '/'
            else:
                # if second part begins with slash, assume missing domain
                if parts[1][0] == '/':
                    account_domain = \
                        _client.get('/v1/user', {})['account']['domain']
                    vault_name, object_path = parts
                # else assumes missing ":" between vault and path
                else:
                    account_domain = parts[0]
                    vault_name, object_path = parts[1].split('/', 1)
        else:
            user = _client.get('/v1/user', {})
            account_domain = user['account']['domain']
            vault_name = 'user-{0}'.format(user['id'])
            object_path = path or '/'

        if object_path[0] != '/':
            object_path = '/' + object_path

        # Strip trailing slash
        if object_path != '/':
            object_path = object_path.rstrip('/')

        full_path = ':'.join([account_domain, vault_name, object_path])
        return full_path, dict(domain=account_domain,
                               vault=vault_name,
                               path=object_path)

    @classmethod
    def get_by_full_path(cls, full_path, **params):
        params.update({'full_path': full_path})
        return cls._retrieve_helper('object', 'full_path', full_path,
                                    **params)

    @classmethod
    def get_by_path(cls, path, **params):
        params.update({'path': path})
        return cls._retrieve_helper('object', 'path', path, **params)

    @classmethod
    def upload_file(cls, local_path, remote_path, vault_name, **kwargs):
        from solvebio import Object, Vault

        _client = kwargs.pop('client', None) or cls._client or client

        try:
            user = _client.get('/v1/user', {})
            account_domain = user['account']['domain']
        except SolveError as e:
            print("Error obtaining account domain: {0}".format(e))
            raise

        local_path = os.path.expanduser(local_path)

        if os.stat(local_path).st_size == 0:
            print('Notice: Cannot upload empty file {0}'.format(local_path))
            return

        # Get MD5, mimetype, and file size for the object
        md5, _ = md5sum(local_path, multipart_threshold=None)
        _, mimetype = mimetypes.guess_type(local_path)
        size = os.path.getsize(local_path)

        vault = Vault.get_by_full_path(vault_name, client=_client)

        if remote_path == '/':
            parent_object_id = None
        else:
            parent_obj = Object.get_by_full_path(':'.join([
                account_domain,
                vault_name,
                remote_path,
            ]), client=_client)
            parent_object_id = parent_obj.id

        description = kwargs.get(
            'description',
            'File uploaded via python client'
        )

        # Create the file, and upload it to the Upload URL
        obj = Object.create(
            vault_id=vault.id,
            parent_object_id=parent_object_id,
            object_type='file',
            filename=os.path.basename(local_path),
            md5=md5,
            mimetype=mimetype,
            size=size,
            description=description,
            client=_client
        )

        print('Notice: File created for {0} at {1}'.format(local_path,
                                                           obj.path))
        print('Notice: Upload initialized')

        upload_url = obj.upload_url

        headers = {
            'Content-MD5': base64.b64encode(binascii.unhexlify(md5)),
            'Content-Type': mimetype,
            'Content-Length': str(size),
        }

        upload_resp = requests.put(upload_url,
                                   data=open(local_path, 'r'),
                                   headers=headers)

        if upload_resp.status_code != 200:
            print('Notice: Upload status code for {0} was {1}'.format(
                local_path, upload_resp.status_code
            ))
            obj.delete(force=True)
        else:
            print('Notice: Successfully uploaded {0} to {1}'.format(local_path,
                                                                    obj.path))

        return obj

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
