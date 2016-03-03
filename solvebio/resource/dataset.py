"""Solvebio Dataset API Resource"""
from ..client import client
from ..help import open_help
from ..query import Query

from .solveobject import convert_to_solve_object
from .apiresource import CreateableAPIResource, ListableAPIResource, \
    UpdateableAPIResource
from .datasetfield import DatasetField

from ..exporters import DatasetExportFile


class Dataset(CreateableAPIResource, ListableAPIResource,
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

    def _data_url(self):
        if 'data_url' not in self:
            if 'id' not in self or not self['id']:
                raise Exception(
                    'No Dataset ID was provided. '
                    'Please instantiate the Dataset '
                    'object with an ID or full_name.')
            # automatically construct the data_url from the ID
            return self.instance_url() + u'/data'
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
            self['beacon_url'] = self.instance_url() + u'/beacon'
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
            self['changelog_url'] = self.instance_url() + u'/changelog'
        if version:
            return self['changelog_url'] + '/' + version
        else:
            return self['changelog_url']

    def changelog(self, version=None, **params):
        # raises an exception if there's no ID
        return client.get(self._changelog_url(version), params)

    def help(self):
        open_help('/library/{0}'.format(self['full_name']))

    def export(self, path, genome_build=None, format='json',
               show_progress=True, download=True):
        if 'exports_url' not in self:
            if 'id' not in self or not self['id']:
                raise Exception(
                    'No Dataset ID was provided. '
                    'Please instantiate the Dataset '
                    'object with an ID or full_name.')
            self['exports_url'] = self.instance_url() + u'/exports'

        print("Exporting dataset {} to {}"
              .format(self['full_name'], path))

        export = client.post(self['exports_url'],
                             {'format': format,
                              'genome_build': genome_build})

        if download:
            manifest = export['manifest']

            for manifest_file in manifest['files']:
                export_file = DatasetExportFile(
                    url=manifest_file['url'],
                    path=path,
                    show_progress=show_progress)

                export_file.download()

                # Validate the MD5 of the downloaded file.
                # Handle's S3's multipart MD5 calculation.
                md5sum, blocks = export_file.md5sum(
                    multipart_threshold=manifest['multipart_threshold_bytes'],
                    multipart_chunksize=manifest['multipart_chunksize_bytes']
                )

                if md5sum != manifest_file['md5']:
                    print("MD5 verification failed for file: {}"
                          .format(export_file.file_name))
                    print("Expected: '{}' Calculated: '{}'"
                          .format(manifest_file['md5'], md5sum))
                    if blocks:
                        print("File is multipart with {} blocks expected. "
                              "Found {} blocks.".format(
                                  manifest_file['multipart_blocks'], blocks))
                else:
                    print("File {} completed downloading and MD5 verification."
                          .format(export_file.file_name))

        return export
