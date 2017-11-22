"""Solvebio Vault API resource"""
from ..client import client
from ..errors import NotFoundError

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

    def __init__(self, vault_id, **kwargs):
        super(Vault, self).__init__(vault_id, **kwargs)

    def _object_list_helper(self, **params):
        from solvebio import Object

        params.update({
            'vault_id': self.id,
        })

        items = Object.all(client=self._client, **params)
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
        return self._object_list_helper(**params)

    def create_dataset(self, **params):
        from solvebio import Dataset, Object

        params.update({'vault_id': self.id})
        path = params.pop('path', None)

        if path == '/' or path is None:
            params['vault_parent_object_id'] = None
        else:
            user = self._client.get('/v1/user', {})
            account_domain = user['account']['domain']

            parent_object = Object.get_by_full_path(':'.join([
                account_domain,
                self.name,
                path,
            ]))

            params['vault_parent_object_id'] = parent_object.id

        return Dataset.create(**params)

    def create_folder(self, **params):
        from solvebio import Object

        params.update({'vault_id': self.id, 'object_type': 'folder'})
        return Object.create(client=self._client, **params)

    def upload_file(self, local_path, remote_path, **kwargs):
        from solvebio import Object
        return Object.upload_file(local_path, remote_path, self.name, **kwargs)

    def search(self, query, **params):
        params.update({
            'query': query,
        })
        return self._object_list_helper(**params)

    @classmethod
    def get_by_full_path(cls, full_path, **kwargs):
        from solvebio import SolveError

        _client = kwargs.pop('client', None) or cls._client or client

        parts = full_path.split(':')

        if len(parts) == 1 or len(parts) == 2:
            if len(parts) == 1:
                try:
                    user = _client.get('/v1/user', {})
                    account_domain = user['account']['domain']
                except SolveError as e:
                    raise Exception("Error obtaining account domain: "
                                    "{0}".format(e))
            else:
                account_domain, full_path = parts

            return Vault._retrieve_helper('vault', 'name', parts[-1],
                                          account_domain=account_domain,
                                          name=parts[-1],
                                          client=_client)
        else:
            raise Exception('Full path must be of the form "vault_name" or '
                            '"account_domain:vault_name"')

    @classmethod
    def get_or_create_by_full_path(cls, full_path, **kwargs):
        _client = kwargs.pop('client', None) or cls._client or client

        try:
            return Vault.get_by_full_path(full_path, client=_client)
        except NotFoundError:
            pass

        # Vault not found, create it

        parts = full_path.split(':', 2)
        vault_name = parts[-1]

        return Vault.create(name=vault_name, client=_client)

    @classmethod
    def get_personal_vault(cls, **kwargs):
        _client = kwargs.pop('client', None) or cls._client or client
        user = _client.get('/v1/user', {})
        # TODO - this will have to change if the format of the personal vaults
        # changes.
        name = 'user-{0}'.format(user['id'])
        vaults = Vault.all(name=name, vault_type='user', client=_client)
        return Vault.retrieve(vaults.data[0].id, client=_client)

    @classmethod
    def get_or_create_uploads_path(cls, **kwargs):
        from solvebio import Object
        _client = kwargs.pop('client', None) or cls._client or client
        v = cls.get_personal_vault(client=_client)
        default_path = 'Uploads'
        full_path = '{0}:/{1}'.format(v.full_path, default_path)

        try:
            upload_dir = Object.get_by_full_path(full_path, client=_client)
        except NotFoundError:
            print("Uploads directory not found. Creating {0}"
                  .format(full_path))
            upload_dir = Object.create(
                vault_id=v.id,
                object_type='folder',
                filename=default_path,
                client=_client
            )

        return upload_dir.path
