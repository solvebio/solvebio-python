"""Solvebio Vault API resource"""
from ..client import client

from .apiresource import CreateableAPIResource
from .apiresource import ListableAPIResource
from .apiresource import SearchableAPIResource
from .apiresource import UpdateableAPIResource
from .apiresource import DeletableAPIResource


class ObjectHelper(object):
    def __init__(self, vault_id):
        self.vault_id = vault_id

    def all(self, **params):
        from solvebio import Object

        if 'vault_id' in params:
            raise Exception('The vault_id is implied and cannot be modified')

        params.update({'vault_id': self.vault_id})
        return Object.all(**params)


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

    def __init__(self, vault_id):
        super(Vault, self).__init__(vault_id)

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

    def ls(self, **params):
        return self._object_list_helper(None, **params)

    @property
    def objects(self):
        return ObjectHelper(self.id)

    def search(self, query, **params):
        params.update({
            'query': query,
        })
        return self._object_list_helper(None, **params)

    @classmethod
    def get_by_name(cls, name):
        from solvebio import SolveError

        parts = name.split(':')

        if len(parts) == 1 or len(parts) == 2:
            if len(parts) == 1:
                name = parts[0]

                try:
                    user = client.get('/v1/user', {})
                    account_domain = user['account']['domain']
                except SolveError as e:
                    raise Exception("Error obtaining account domain: "
                                    "{0}".format(e))
            else:
                account_domain, name = parts

            vaults = Vault.all(account_domain=account_domain, name=name)

            if len(vaults.data) == 0:
                raise Exception('Vault does not exist with name "{0}" '
                                'for domain "{1}"'.format(name,
                                                          account_domain))
            else:
                return Vault.retrieve(vaults.data[0].id)
        else:
            raise Exception('Name must be of the form "name" or '
                            '"account:vault_name"')

    @classmethod
    def get_personal_vault(cls):
        user = client.get('/v1/user', {})
        # TODO - this will have to change if the format of the personal vaults
        # changes.
        name = 'user-{0}'.format(user['id'])
        vaults = Vault.all(name=name)
        return Vault.retrieve(vaults.data[0].id)
