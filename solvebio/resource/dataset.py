import os
import time

from ..client import client
from ..query import Query
from ..errors import NotFoundError

from .solveobject import convert_to_solve_object
from .apiresource import CreateableAPIResource
from .apiresource import ListableAPIResource
from .apiresource import UpdateableAPIResource
from .apiresource import DeletableAPIResource

from .task import Task
from .datasetfield import DatasetField
from .datasetexport import DatasetExport
from .datasetmigration import DatasetMigration


class Dataset(CreateableAPIResource,
              ListableAPIResource,
              DeletableAPIResource,
              UpdateableAPIResource):
    """
    Datasets are access points to data. Dataset names are unique
    within a vault folder.
    """
    RESOURCE_VERSION = 2

    LIST_FIELDS = (
        ('id', 'ID'),
        ('vault_name', 'Vault'),
        ('vault_object_path', 'Path'),
        ('documents_count', 'Documents'),
        ('description', 'Description'),
    )

    @classmethod
    def make_full_path(cls, vault_name, path, name, **kwargs):
        from solvebio import SolveError

        _client = kwargs.pop('client', None) or cls._client or client

        try:
            user = _client.get('/v1/user', {})
            domain = user['account']['domain']
        except SolveError as e:
            print("Error obtaining account domain: {0}".format(e))
            raise

        result = ':'.join([
            domain,
            vault_name,
            os.path.join('/' + path.lstrip('/'), name),
        ])

        return result

    @classmethod
    def get_by_full_path(cls, full_path, **kwargs):
        from solvebio import Object

        _client = kwargs.pop('client', None) or cls._client or client
        obj = Object.get_by_full_path(full_path, assert_type='dataset',
                                      client=_client)
        return Dataset.retrieve(obj['dataset_id'], client=_client, **kwargs)

    @classmethod
    def get_or_create_by_full_path(cls, full_path, **kwargs):
        from solvebio import Vault
        from solvebio import Object

        _client = kwargs.pop('client', None) or cls._client or client
        create_vault = kwargs.pop('create_vault', False)
        create_folders = kwargs.pop('create_folders', True)

        try:
            return Dataset.get_by_full_path(full_path, assert_type='dataset',
                                            client=_client)
        except NotFoundError:
            pass

        # Dataset not found, create it step-by-step
        full_path, parts = Object.validate_full_path(full_path, client=_client)

        if create_vault:
            vault = Vault.get_or_create_by_full_path(
                '{0}:{1}'.format(parts['domain'], parts['vault']),
                client=_client)
        else:
            vaults = Vault.all(account_domain=parts['domain'],
                               name=parts['vault'],
                               client=_client)
            if len(vaults.solve_objects()) == 0:
                raise Exception(
                    'Vault does not exist with name {0}:{1}'.format(
                        parts['domain'], parts['vault'])
                )
            vault = vaults.solve_objects()[0]

        # Create the folders to hold the dataset if they do not already exist.
        object_path = parts['path']
        curr_path = os.path.dirname(object_path)
        folders_to_create = []
        new_folders = []
        id_map = {'/': None}

        while curr_path != '/':
            try:
                obj = Object.get_by_path(curr_path,
                                         vault_id=vault.id,
                                         assert_type='folder',
                                         client=_client)
                id_map[curr_path] = obj.id
                break
            except NotFoundError:
                if not create_folders:
                    raise Exception('Folder {} does not exist.  Pass '
                                    'create_folders=True to auto-create '
                                    'missing folders')

                folders_to_create.append(curr_path)
                curr_path = '/'.join(curr_path.split('/')[:-1])
                if curr_path == '':
                    break

        for folder in reversed(folders_to_create):
            new_folder = Object.create(
                object_type='folder',
                vault_id=vault.id,
                filename=os.path.basename(folder),
                parent_object_id=id_map[os.path.dirname(folder)],
                client=_client
            )
            new_folders.append(new_folder)
            id_map[folder] = new_folder.id

        if os.path.dirname(object_path) == '/':
            parent_folder_id = None
        elif new_folders:
            parent_folder_id = new_folders[-1].id
        else:
            parent_folder_id = id_map[os.path.dirname(object_path)]

        return Dataset.create(name=os.path.basename(object_path),
                              vault_id=vault.id,
                              vault_parent_object_id=parent_folder_id,
                              client=_client,
                              **kwargs)

    def saved_queries(self, **params):
        from solvebio import SavedQuery

        if 'id' not in self or not self['id']:
            raise Exception(
                'No Dataset ID was provided. '
                'Please instantiate the Dataset '
                'object with an ID.')

        saved_queries = SavedQuery.all(
            dataset_id=self['id'],
            client=self._client,
            **params)

        return saved_queries

    def fields(self, name=None, **params):
        if 'fields_url' not in self:
            raise Exception(
                'Please use Dataset.retrieve({ID}) before looking '
                'up fields')

        if name:
            params.update({
                'name': name,
            })
            fields = self._client.get(self.fields_url, params)
            result = DatasetField.retrieve(fields['data'][0]['id'],
                                           client=self._client)
            return result

        response = self._client.get(self.fields_url, params)
        results = convert_to_solve_object(response, client=self._client)
        results.set_tabulate(
            ['name', 'data_type', 'entity_type', 'description'],
            headers=['Field', 'Data Type', 'Entity Type', 'Description'],
            aligns=['left', 'left', 'left', 'left'], sort=True)

        return results

    def template(self, **params):
        if 'template_url' not in self:
            raise Exception(
                'Please use Dataset.retrieve({ID}) before retrieving '
                'a template')

        response = self._client.get(self.template_url, params)
        return convert_to_solve_object(response, client=self._client)

    def commits(self, **params):
        if 'commits_url' not in self:
            raise Exception(
                'Please use Dataset.retrieve({ID}) before looking '
                'up commits')

        response = self._client.get(self.commits_url, params)
        results = convert_to_solve_object(response, client=self._client)
        results.set_tabulate(
            ['id', 'title', 'description', 'status', 'created_at'],
            headers=['ID', 'Title', 'Description', 'Status', 'Created'],
            aligns=['left', 'left', 'left', 'left', 'left'], sort=False)

        return results

    def imports(self, **params):
        if 'imports_url' not in self:
            raise Exception(
                'Please use Dataset.retrieve({ID}) before looking '
                'up imports')

        response = self._client.get(self.imports_url, params)
        results = convert_to_solve_object(response, client=self._client)
        results.set_tabulate(
            ['id', 'title', 'description', 'status', 'created_at'],
            headers=['ID', 'Title', 'Description', 'Status', 'Created'],
            aligns=['left', 'left', 'left', 'left', 'left'], sort=False)

        return results

    def _data_url(self):
        if 'data_url' not in self:
            if 'id' not in self or not self['id']:
                raise Exception(
                    'No Dataset ID was provided. '
                    'Please instantiate the Dataset '
                    'object with an ID.')
            # automatically construct the data_url from the ID
            return self.instance_url() + '/data'
        return self['data_url']

    def query(self, query=None, **params):
        self._data_url()  # raises an exception if there's no ID
        return Query(self['id'], query=query, client=self._client, **params)

    def lookup(self, *sbids):
        lookup_url = self._data_url() + '/' + ','.join(sbids)
        return self._client.get(lookup_url, {})['results']

    def _beacon_url(self):
        if 'beacon_url' not in self:
            if 'id' not in self or not self['id']:
                raise Exception(
                    'No Dataset ID was provided. '
                    'Please instantiate the Dataset '
                    'object with an ID.')
            # automatically construct the data_url from the ID
            self['beacon_url'] = self.instance_url() + '/beacon'
        return self['beacon_url']

    def beacon(self, **params):
        # raises an exception if there's no ID
        return self._client.get(self._beacon_url(), params)

    def import_file(self, path, **kwargs):
        """
        This is a shortcut to creating a DatasetImport. Can't use "import()"
        because of Python.
        """
        from . import Manifest
        from . import DatasetImport

        if 'id' not in self or not self['id']:
            raise Exception(
                'No Dataset ID found. '
                'Please instantiate or retrieve a dataset '
                'with an ID.')

        manifest = Manifest()
        manifest.add(path)
        return DatasetImport.create(
            dataset_id=self['id'],
            manifest=manifest.manifest,
            **kwargs)

    def export(self, format='json', follow=True, **kwargs):
        if 'id' not in self or not self['id']:
            raise Exception(
                'No Dataset ID was provided. '
                'Please instantiate the Dataset '
                'object with an ID.')

        export = DatasetExport.create(
            dataset_id=self['id'],
            format=format,
            **kwargs)

        if follow:
            export.follow()

        return export

    def migrate(self, target, follow=True, **kwargs):
        """
        Migrate the data from this dataset to a target dataset.

        Valid optional kwargs include:

        * source_params
        * target_fields
        * include_errors
        * commit_mode

        """
        if 'id' not in self or not self['id']:
            raise Exception(
                'No source dataset ID found. '
                'Please instantiate the Dataset '
                'object with an ID.')

        # Target can be provided as a Dataset, or as an ID.
        if isinstance(target, Dataset):
            target_id = target.id
        else:
            target_id = target

        migration = DatasetMigration.create(
            source_id=self['id'],
            target_id=target_id,
            **kwargs)

        if follow:
            migration.follow()

        return migration

    def activity(self, follow=False):
        statuses = ['running', 'queued', 'pending']
        activity = list(Task.all(target_object_id=self.id,
                                 status=','.join(statuses),
                                 client=self._client))

        print("Found {0} active task(s)".format(len(activity)))
        if not follow:
            return activity

        while True:
            if not activity:
                break

            for task in activity:
                task.follow()

            time.sleep(5.0)
            activity = self.activity()

        return activity

    #
    # Vault properties
    #
    @property
    def vault_object(self):
        from solvebio import Object
        return Object.retrieve(self['vault_object_id'], client=self._client)
