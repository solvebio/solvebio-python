import time

from ..client import client
from ..help import open_help
from ..query import Query

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
    USES_V2_ENDPOINT = True

    LIST_FIELDS = (
        ('id', 'ID'),
        ('vault_object_name', 'Name'),
        ('description', 'Description'),
    )

    @classmethod
    def get_by_full_path(cls, full_path, **kwargs):
        from solvebio import Object
        from solvebio import SolveError

        try:
            obj = Object.retrieve_by_full_path(full_path)
            dataset = Dataset.retrieve(obj['dataset_id'], **kwargs)
            return dataset
        except SolveError as e:
            if e.status_code != 404:
                raise e

    @classmethod
    def create_by_name(cls, name, vault_name, path, **kwargs):
        from solvebio import Vault
        from solvebio import Object
        from solvebio import SolveError

        vaults = Vault.all(name=vault_name)
        if len(vaults) == 0:
            # @davecap - should I auto-create the vault here instead?
            raise Exception('Vault not found with name {}'.format(
                vault_name))
        else:
            vault_id = vaults[0]['id']

        if not path or path == '/':
            vault_parent_object_id = None
        else:
            objects = Object.all(vault_id=vault_id, path=path,
                                 object_type='folder')
            # TODO - remove object_type folder and raise exception if object
            #  exists but is not object_type = folder
            if len(objects) == 0:
                # @davecap - should I auto-create the folder here instead?
                raise Exception('Path {} not found in vault {}'.format(
                    path, vault_name))
            else:
                vault_parent_object_id = objects[0]['id']

        return Dataset.create(name=name,
                              vault_id=vault_id,
                              vault_parent_object_id=vault_parent_object_id,
                              **kwargs)

    def fields(self, name=None, **params):
        if 'fields_url' not in self:
            raise Exception(
                'Please use Dataset.retrieve({ID}) before looking '
                'up fields')

        if name:
            fields = client.get(self.fields_url, params)
            for i in fields['data']:
                if i['name'] == name:
                    result = DatasetField.retrieve(i['id'], **params)
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
        print 'burl', self['beacon_url']
        return self['beacon_url']

    def beacon(self, **params):
        # raises an exception if there's no ID
        print 'and params are', params
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
        * auto_approve
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

        while True:
            for task in active_tasks:
                task.follow()

            time.sleep(5.0)
            active_tasks = self.tasks()
            if not active_tasks:
                break

        return active_tasks
