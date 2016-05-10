from ..client import client
from ..help import open_help
from ..query import Query
from ..utils.humanize import naturalsize
from ..utils.md5sum import md5sum

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

    def export(self, path, genome_build=None, format='json',
               show_progress=True, download=True):
        if 'exports_url' not in self:
            if 'id' not in self or not self['id']:
                raise Exception(
                    'No Dataset ID was provided. '
                    'Please instantiate the Dataset '
                    'object with an ID or full_name.')
            self['exports_url'] = self.instance_url() + '/exports'

        export = client.post(self['exports_url'],
                             {'format': format,
                              'genome_build': genome_build})

        print("Exporting dataset {0} to {1}"
              .format(self['full_name'], path))

        total_size = 0
        manifest = export['manifest']

        for i, manifest_file in enumerate(manifest['files']):
            total_size += manifest_file['size']
            export_file = DatasetExportFile(
                url=manifest_file['url'],
                path=path,
                show_progress=show_progress)

            if not download:
                print('Downloading is off, skipping file {0} ({1})'
                      .format(export_file.file_name,
                              naturalsize(manifest_file['size'])))
                continue

            print('Downloading file {0}/{1}: {2} ({3})'
                  .format(i + 1, len(manifest['files']),
                          export_file.file_name,
                          naturalsize(manifest_file['size'])))
            export_file.download()

            # Validate the MD5 of the downloaded file.
            # Handle's S3's multipart MD5 calculation.
            md5, blocks = md5sum(
                multipart_threshold=manifest['multipart_threshold_bytes'],
                multipart_chunksize=manifest['multipart_chunksize_bytes']
            )

            if md5 != manifest_file['md5']:
                print("### Export failed MD5 verification!")
                print("### -------------------------------")
                print("### File: {0}".format(export_file.file_name))
                print("### Expected MD5: {0}".format(manifest_file['md5']))
                print("### Calculated MD5: {0}".format(md5))
                if blocks and manifest_file['multipart_blocks'] != blocks:
                    print("### Multipart block size failed verification")
                    print("### Expected: {0} blocks"
                          .format(manifest_file['multipart_blocks']))
                    print("### Found: {0} blocks".format(blocks))
                print("\n### Delete the following file and try again: {0}"
                      .format(export_file.file_name))
                print("### If the problem persists, please email "
                      "support@solvebio.com")
                return None

            print("File {0} completed downloading and MD5 verification."
                  .format(export_file.file_name))

        print('Number of files: {0}'.format(len(manifest['files'])))
        print('Number of records: {0}'.format(export['documents_count']))
        print('Total size: {0}'.format(naturalsize(total_size)))

        return export
