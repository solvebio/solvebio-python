from .apiresource import ListableAPIResource
from .apiresource import DeletableAPIResource
from .apiresource import UpdateableAPIResource
from .apiresource import CreateableAPIResource
from .solveobject import convert_to_solve_object


class Group(CreateableAPIResource, ListableAPIResource,
            UpdateableAPIResource, DeletableAPIResource):
    """
    A Group represents a group of users with shared permissions for a vault.
    """
    RESOURCE_VERSION = 1

    LIST_FIELDS = (
        ('id', 'ID'),
        ('name', 'Name'),
        ('memberships_count', 'Members'),
        ('vaults_count', 'Vaults'),
        ('role', 'Role'),
        ('description', 'Description'),
    )

    def members(self, **params):
        response = self._client.get(self.memberships_url, params)
        results = convert_to_solve_object(response, client=self._client)
        results.set_tabulate(
            ['id', 'full_name', 'username', 'email', 'role'],
            headers=['ID', 'Full Name', 'Username', 'Email', 'Role'],
            aligns=['left', 'left', 'left', 'left', 'left'], sort=False)

        return results

    def _get_vaults(self, **params):
        response = self._client.get(self.vaults_url, params)
        return convert_to_solve_object(response, client=self._client)

    def vaults(self, **params):
        results = self._get_vaults(**params)
        results.set_tabulate(
            ['id', 'name', 'permission', 'vault_permissions'],
            headers=['ID', 'Vault', 'Permission', 'Permissions Detail'],
            aligns=['left', 'left', 'left', 'left'], sort=False)

        return results

    def datasets(self, **params):
        from . import Object
        vaults = self._get_vaults(**params)
        objects_url = Object.class_url() + '?object_type=dataset&' + \
            '&'.join(['vault_id={0}'.format(v.id) for v in vaults])
        response = self._client.get(objects_url, params)
        datasets = convert_to_solve_object(response, client=self._client)
        datasets.set_tabulate(
            ['id', 'vault_name', 'path',
             'dataset_documents_count', 'dataset_description'],
            headers=['ID', 'Vault', 'Path', 'Documents', 'Description'],
            aligns=['left', 'left', 'left', 'left', 'left'], sort=False)

        return datasets
