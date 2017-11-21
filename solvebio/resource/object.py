"""Solvebio Object API resource"""
import os
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


class Object(CreateableAPIResource,
             ListableAPIResource,
             DeletableAPIResource,
             SearchableAPIResource,
             UpdateableAPIResource):
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

        md5, _ = md5sum(local_path, multipart_threshold=None)
        _, mimetype = mimetypes.guess_type(local_path)
        size = os.path.getsize(local_path)

        if md5sum('/dev/null')[0] == md5:
            print('Notice: Cannot upload empty file {0}'.format(local_path))
            return

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
