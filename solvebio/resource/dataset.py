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
from .datasetfield import DatasetField
from .datasetimport import DatasetImport
from .datasetcommit import DatasetCommit
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

        obj = Object.get_by_full_path(full_path)
        dataset = Dataset.retrieve(obj['dataset_id'], **kwargs)
        return dataset

    @classmethod
    def get_or_create(cls, vault_name, path, name, **kwargs):
        from solvebio import Vault
        from solvebio import Object
        from solvebio import SolveError

        create_vault = kwargs.pop('create_vault', False)

        if path[0] != '/':
            raise Exception(
                'Paths are absolute and must begin with a "/"'
            )

        # Remove double slashes and strip trailing slash
        path = re.sub('//+', '/', path)
        if path != '/':
            path = path.rstrip('/')

        try:
            test_path = Dataset.make_full_path(vault_name, path, name)
        except SolveError as e:
            print("Error obtaining account domain: {0}".format(e))
            raise

        try:
            dataset = Dataset.get_by_full_path(test_path)

            # If the dataset exists but the genome_builds don't match,
            # update it with the new builds.
            if dataset.is_genomic and \
                    dataset.genome_builds != kwargs.get('genome_builds'):
                dataset.genome_builds = kwargs.get('genome_builds')
                dataset.save()

            return dataset
        except NotFoundError:
            pass

        # Dataset not found, create it step-by-step
        vaults = Vault.all(name=vault_name)
        if len(vaults.solve_objects()) == 0:
            if create_vault:
                vault = Vault.create(name=vault_name,
                                     require_unique_paths=True,
                                     is_public=False,
                                     vault_type='general',
                                     provider='SolveBio')
            else:
                raise Exception('Vault does not exist with name {0}'.format(
                    vault_name))
        else:
            vault = vaults.solve_objects()[0]
            if vault.name.lower() != vault_name.lower():
                raise Exception('Vault name from API does not match '
                                'user-provided value')

        # Create the folders to hold the dataset if they do not already exist.
        curr_path = path
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

        if path == '/':
            parent_folder_id = None
        elif new_folders:
            parent_folder_id = new_folders[-1].id
        else:
            parent_folder_id = id_map[path]

        return Dataset.create(name=name,
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
            ['name', 'data_type', 'description'],
            headers=['Field', 'Data Type', 'Description'],
            aligns=['left', 'left', 'left'], sort=True)

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

    def tasks(self, follow=False):
        statuses = ['running', 'queued', 'pending']
        active_tasks = \
            list(DatasetImport.all(dataset=self.id, status=statuses)) + \
            list(DatasetCommit.all(dataset=self.id, status=statuses)) + \
            list(DatasetExport.all(dataset=self.id, status=statuses)) + \
            list(DatasetMigration.all(target=self.id, status=statuses))

        if not follow:
            return active_tasks
        else:
            print("Found {0} active tasks".format(len(active_tasks)))

        while True:
            for task in active_tasks:
                task.follow()

            time.sleep(5.0)
            active_tasks = self.tasks()
            if not active_tasks:
                break

        return active_tasks
