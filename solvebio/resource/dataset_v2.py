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
    within versions of a depository.
    """
    LIST_FIELDS = (
        ('full_name', 'Name'),
        ('depository', 'Depository'),
        ('title', 'Title'),
        ('description', 'Description'),
    )

    @classmethod
    def get_or_create_by_full_name(cls, full_name, **kwargs):
        from solvebio import Depository
        from solvebio import DepositoryVersion
        from solvebio import SolveError

        try:
            dataset = Dataset.retrieve(full_name)
            # If the dataset exists but the genome_builds don't match,
            # update it with the new builds.
            if dataset.is_genomic and \
                    dataset.genome_builds != kwargs.get('genome_builds'):
                dataset.genome_builds = kwargs.get('genome_builds')
                dataset.save()

            return dataset
        except SolveError as e:
            if e.status_code != 404:
                raise e

        # Dataset not found, create it step-by-step
        try:
            # Split the name into parts
            depo, version, dataset_name = full_name.split('/')
        except ValueError:
            raise ValueError(
                "Invalid dataset name '{0}'. Please ensure that it is "
                "in the following format: "
                "'<depository>/<version>/<dataset>'"
                .format(full_name))

        try:
            depo = Depository.retrieve(depo)
        except SolveError as e:
            if e.status_code != 404:
                raise e
            depo = Depository.create(name=depo, title=depo)

        try:
            version = DepositoryVersion.retrieve(
                '{0}/{1}'.format(depo.name, version))
        except SolveError as e:
            if e.status_code != 404:
                raise e
            version = DepositoryVersion.create(
                depository_id=depo.id, name=version, title=version)

        # Use a default title (dataset name) if none is provided
        title = kwargs.pop('title', dataset_name)
        return Dataset.create(
            depository_version_id=version.id,
            name=dataset_name, title=title, **kwargs)

    def depository_version(self):
        from .depositoryversion import DepositoryVersion
        return DepositoryVersion.retrieve(self['depository_version'])

    def depository(self):
        from .depository import Depository
        return Depository.retrieve(self['depository'])

    def fields(self, name=None, **params):
        if 'fields_url' not in self:
            raise Exception(
                'Please use Dataset.retrieve({ID}) before looking '
                'up fields')

        if name:
            # construct the field's full_name if a field name is provided
            return DatasetField.retrieve(
                '/'.join([self['full_name'], name]))

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
                    'object with an ID or full_name.')
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
                    'object with an ID or full_name.')
            # automatically construct the data_url from the ID
            self['beacon_url'] = self.instance_url() + '/beacon'
        return self['beacon_url']

    def beacon(self, **params):
        # raises an exception if there's no ID
        return client.get(self._beacon_url(), params)

    def _changelog_url(self, version=None):
        if 'changelog_url' not in self:
            if 'id' not in self or not self['id']:
                raise Exception(
                    'No Dataset ID was provided. '
                    'Please instantiate the Dataset '
                    'object with an ID or full_name.')
            # automatically construct the data_url from the ID
            self['changelog_url'] = self.instance_url() + '/changelog'
        if version:
            return self['changelog_url'] + '/' + version
        else:
            return self['changelog_url']

    def changelog(self, version=None, **params):
        # raises an exception if there's no ID
        return client.get(self._changelog_url(version), params)

    def help(self):
        open_help('/library/{0}'.format(self['full_name']))

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
                'with an ID or full_name.')

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
                'object with an ID or full_name.')

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
                'object with an ID or full_name.')

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
