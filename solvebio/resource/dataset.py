import os
import re
import time

from ..client import client
from ..help import open_help
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
    PRINTABLE_NAME = 'dataset'

    LIST_FIELDS = (
        ('id', 'ID'),
        ('vault_name', 'Vault Name'),
        ('vault_object_path', 'Vault Object Path'),
        ('vault_object_filename', 'Vault Object Filename'),
        ('created_at', 'Created'),
        ('description', 'Description'),
    )

    @classmethod
    def make_full_path(cls, vault_name, path, name):
        from solvebio import SolveError

        try:
            user = client.get('/v1/user', {})
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

        parts = full_path.split(':', 2)

        if len(parts) == 3:
            account_domain, vault_name, object_path = parts
        elif len(parts) == 2:
            vault_name, object_path = parts
            user = client.get('/v1/user', {})
            account_domain = user['account']['domain']
        else:
            raise Exception('Full path must be of the format: '
                            '"vault_name:object_path" or '
                            '"account_domain:vault_name:object_path"')

        if object_path[0] != '/':
            raise Exception(
                'Paths are absolute and must begin with a "/"'
            )

        # Remove double slashes and strip trailing slash
        object_path = re.sub('//+', '/', object_path)
        if object_path != '/':
            object_path = object_path.rstrip('/')

        test_path = ':'.join([account_domain, vault_name, object_path])
        obj = Object.get_by_full_path(test_path)
        dataset = Dataset.retrieve(obj['dataset_id'], **kwargs)
        return dataset

    @classmethod
    def get_or_create_by_full_path(cls, full_path, **kwargs):
        from solvebio import Vault
        from solvebio import Object

        create_vault = kwargs.pop('create_vault', False)
        create_folders = kwargs.pop('create_folders', True)

        try:
            return Dataset.get_by_full_path(full_path)
        except NotFoundError:
            pass

        # Dataset not found, create it step-by-step

        parts = full_path.split(':', 2)

        if len(parts) == 3:
            account_domain, vault_name, object_path = parts
        elif len(parts) == 2:
            vault_name, object_path = parts
            user = client.get('/v1/user', {})
            account_domain = user['account']['domain']

        vaults = Vault.all(account_domain=account_domain, name=vault_name)

        if len(vaults.solve_objects()) == 0:
            if create_vault:
                vault = Vault.create(name=vault_name)
            else:
                raise Exception('Vault does not exist with name {0}'.format(
                    vault_name))
        else:
            vault = vaults.solve_objects()[0]
            if vault.name.lower() != vault_name.lower():
                raise Exception('Vault name from API does not match '
                                'user-provided value')

        # Create the folders to hold the dataset if they do not already exist.
        curr_path = os.path.dirname(object_path)
        folders_to_create = []
        new_folders = []
        id_map = {'/': None}

        while curr_path != '/':
            try:
                obj = Object.get_by_path(curr_path,
                                         vault_id=vault.id)
                if obj.object_type != 'folder':
                    raise Exception(
                        'Path {0} is a {1} and not a folder'.format(
                            obj.path, obj.object_type)
                    )
                else:
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
                              **kwargs)

    def fields(self, name=None, **params):
        if 'fields_url' not in self:
            raise Exception(
                'Please use Dataset.retrieve({ID}) before looking '
                'up fields')

        if name:
            params.update({
                'name': name,
            })
            fields = client.get(self.fields_url, params)
            result = DatasetField.retrieve(fields['data'][0]['id'])
            return result

        response = client.get(self.fields_url, params)
        results = convert_to_solve_object(response)
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

        response = client.get(self.template_url, params)
        return convert_to_solve_object(response)

    def commits(self, **params):
        if 'commits_url' not in self:
            raise Exception(
                'Please use Dataset.retrieve({ID}) before looking '
                'up commits')

        response = client.get(self.commits_url, params)
        results = convert_to_solve_object(response)
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

        response = client.get(self.imports_url, params)
        results = convert_to_solve_object(response)
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
        return Query(self['id'], query=query, **params)

    def lookup(self, *sbids):
        lookup_url = self._data_url() + '/' + ','.join(sbids)
        return client.get(lookup_url, {})['results']

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
        return client.get(self._beacon_url(), params)

    def help(self):
        open_help('/library/{0}'.format(self['id']))

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
        activity = list(Task.all(target_object=self.id,
                                 status=','.join(statuses)))

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
