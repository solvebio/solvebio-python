"""Solvebio Vault API resource"""
from ..client import client

from .apiresource import CreateableAPIResource
from .apiresource import ListableAPIResource
from .apiresource import SearchableAPIResource
from .apiresource import UpdateableAPIResource
from .apiresource import DeletableAPIResource


class Vault(CreateableAPIResource,
            ListableAPIResource,
            DeletableAPIResource,
            SearchableAPIResource,
            UpdateableAPIResource):
    """
    A vault is like a filesystem that can contain files, folder,
    and SolveBio datasets.  Vaults can be "connected" to external resources
    such as DNAnexus and SevenBridges projects, or Amazon S3 Buckets.
    Typically, vaults contain a series of datasets that are compatible with
    each other (i.e. they come from the same data source or project).
    """
    RESOURCE_VERSION = 2

    LIST_FIELDS = (
        ('id', 'ID'),
        ('name', 'Name'),
        ('is_public', 'Is Public'),
        ('vault_type', 'Vault Type'),
        ('description', 'Description'),
    )

    def _object_list_helper(self, object_type, **params):
        from solvebio import Object

        params.update({
            'vault_id': self.id,
        })

        if object_type:
            params.update({
                'object_type': object_type,
            })

        items = Object.all(**params)

        return items

    def files(self, **params):
        return self._object_list_helper('file', **params)

    def folders(self, **params):
        return self._object_list_helper('folder', **params)

    def datasets(self, **params):
        return self._object_list_helper('dataset', **params)

    def objects(self, **params):
        print 'id is', self.id
        return self._object_list_helper(None, **params)

    def search(self, query, **params):
        params.update({
            'query': query,
        })
        return self._object_list_helper(None, **params)

    @classmethod
    def get_personal_vault(cls):
        user = client.get('/v1/user', {})
        # TODO - this will have to change if the format of the personal vaults
        # changes.
        name = 'user-{}'.format(user['id'])
        vaults = Vault.all(name=name)
        return Vault.retrieve(vaults.data[0].id)
