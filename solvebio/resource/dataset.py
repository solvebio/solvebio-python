import os
import time

from ..client import client
from ..query import Query

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
        from solvebio import Object

        # Assert this is a dataset (for the "get" in get_or_create)
        kwargs['assert_type'] = 'dataset'
        # Create this is a dataset (for the "create" in get_or_create)
        kwargs['object_type'] = 'dataset'

        _client = kwargs.pop('client', None) or cls._client or client
        obj = Object.get_or_create_by_full_path(
            full_path, client=_client, **kwargs)

        return cls.retrieve(obj.dataset_id)

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
            # Dataset object may not have been retrieved. Grab it.
            self.refresh()

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
            # Dataset object may not have been retrieved. Grab it.
            self.refresh()

        response = self._client.get(self.template_url, params)
        return convert_to_solve_object(response, client=self._client)

    def commits(self, **params):
        if 'commits_url' not in self:
            # Dataset object may not have been retrieved. Grab it.
            self.refresh()

        response = self._client.get(self.commits_url, params)
        results = convert_to_solve_object(response, client=self._client)
        results.set_tabulate(
            ['id', 'title', 'description', 'status', 'created_at'],
            headers=['ID', 'Title', 'Description', 'Status', 'Created'],
            aligns=['left', 'left', 'left', 'left', 'left'], sort=False)

        return results

    def imports(self, **params):
        if 'imports_url' not in self:
            # Dataset object may not have been retrieved. Grab it.
            self.refresh()

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

        # Target can be provided as an object or as an ID.
        try:
            target_id = target.id
        except AttributeError:
            target_id = target

        migration_resp = DatasetMigration.create(
            source_id=self['id'],
            target_id=target_id,
            **kwargs)

        if follow:
            # If migration was created with the parallel flag, then multiple
            # migration objects will be returned.
            if "data" in migration_resp:
                for migration in migration_resp["data"]:
                    migration.follow()
            else:
                migration_resp.follow()

        return migration_resp

    def archive(self, storage_class=None, follow=False):
        """
        Archive this dataset
        """
        return self.vault_object.archive(storage_class=storage_class, follow=follow)

    def restore(self, storage_class=None, follow=False, **kwargs):
        """
        Restore this dataset
        """
        return self.vault_object.restore(storage_class=storage_class, follow=follow)

    def activity(self, follow=False, limit=1,
                 sleep_seconds=Task.SLEEP_WAIT_DEFAULT):
        """Get a list of active Tasks that have a target object of
        the dataset. Active tasks are in the running, queued or pending state.

        Defaults to limit=1 for performance. Increase this value in order
        to return more tasks as output.
        """
        statuses = ['running', 'queued', 'pending']

        while True:

            # NOTE: source_object_id is not being queried here
            # and therefore active DatasetExports will not appear
            # in activity
            activity = Task.all(target_object_id=self.id,
                                status=','.join(statuses),
                                limit=limit,
                                ordering='-updated_at',
                                client=self._client)

            print("Found {0} active task(s)".format(activity.total))
            if not activity or not follow:
                break

            for task in activity.solve_objects()[0:limit]:
                task.follow(sleep_seconds=sleep_seconds)

            time.sleep(sleep_seconds)

        return list(activity)

    #
    # Vault properties
    #
    @property
    def vault_object(self):
        from solvebio import Object
        return Object.retrieve(self['vault_object_id'], client=self._client)

    def enable_global_beacon(self):
        """
        Enable Global Beacon for this dataset.
        """
        return self.vault_object.enable_global_beacon()

    def disable_global_beacon(self):
        """
        Disable Global Beacon for this dataset.
        """
        return self.vault_object.disable_global_beacon()

    def get_global_beacon_status(self, raise_on_disabled=False):
        """
        Retrieves the Global Beacon status for this dataset.
        """
        return self.vault_object.get_global_beacon_status(raise_on_disabled)
