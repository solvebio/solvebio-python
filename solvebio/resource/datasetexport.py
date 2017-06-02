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
    LIST_FIELDS = (
        ('id', 'ID'),
        ('title', 'Title'),
        ('description', 'Description'),
        ('status', 'Status'),
        ('created_at', 'Created'),
    )

    def dataset(self):
        from .dataset import Dataset
        return Dataset.retrieve(self['dataset'])

    def follow(self):
        print("View your export status on MESH: "
              "https://my.solvebio.com/jobs/export/{0}"
              .format(self.id))

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
                              self.metadata['progress']['processed_records'],
                              self.documents_count))

            time.sleep(3)
            self.refresh()

        if self.status == 'completed':
            print("Export complete!")
