from .apiresource import CreateableAPIResource
from .apiresource import ListableAPIResource
from .apiresource import DeletableAPIResource
from .apiresource import DownloadableAPIResource

import time


class DatasetExport(CreateableAPIResource, ListableAPIResource,
                    DownloadableAPIResource, DeletableAPIResource):
    """
    DatasetExport represent an export task that takes
    a Dataset or filtered Dataset (Query) and exports
    the contents to a flat file (CSV, JSON, or XLSX).

    For interactive use, DatasetExport can be "followed" to watch
    the progression of the task.
    """
    RESOURCE_VERSION = 2
    PRINTABLE_NAME = 'dataset export'

    LIST_FIELDS = (
        ('id', 'ID'),
        ('documents_count', 'Records'),
        ('format', 'Format'),
        ('status', 'Status'),
        ('created_at', 'Created'),
    )

    def dataset(self):
        from .dataset import Dataset
        return Dataset.retrieve(self['dataset'])

    def follow(self, loop=True):
        if self.status == 'queued':
            print("Waiting for export (id = {0}) to start..."
                  .format(self.id))

        export_status = self.status
        while self.status in ['queued', 'running']:
            if self.status != export_status:
                print("Export is now {0} (was {1})"
                      .format(self.status, export_status))
                export_status = self.status

            if self.status == 'running':
                print("Export '{0}' is {1}: {2}/{3} records exported"
                      .format(self.id,
                              self.status,
                              self.metadata.get('progress', {}).get('processed_records', 0),  # noqa
                              self.documents_count))

            if not loop:
                return

            time.sleep(3)
            self.refresh()

        if self.status == 'completed':
            print('Export complete! Run <export_obj>'
                  '.download(path=<some_path>) to download.')
