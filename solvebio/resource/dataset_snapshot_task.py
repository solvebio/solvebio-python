from .apiresource import ListableAPIResource
from .apiresource import CreateableAPIResource
from .solveobject import convert_to_solve_object

import time


class DatasetSnapshotTask(CreateableAPIResource, ListableAPIResource):
    """
    DatasetSnapshotTask represents the task to snapshot and archive a dataset
    """
    RESOURCE_VERSION = 2

    LIST_FIELDS = (
        ('id', 'ID'),
        ('dataset_id', 'Dataset'),
        ('vault_id', 'Vault'),
        ('status', 'Status'),
        ('created_at', 'Created'),
    )

    @property
    def dataset(self):
        response = self._client.get(self['dataset']['url'], {})
        return convert_to_solve_object(response, client=self._client)

    def follow(self, loop=True):
        if self.status == 'queued':
            print("Waiting for Dataset Snapshot task (id = {0}) to start..."
                  .format(self.id))

        status = self.status
        while self.status in ['queued', 'running']:
            if self.status != status:
                print("Snapshot is now {0} (was {1})"
                      .format(self.status, status))
                status = self.status

            if self.status == 'running':
                print("Snapshot '{0}' is {1}".format(self.id, self.status))

            if not loop:
                return

            time.sleep(3)
            self.refresh()

        if self.status == 'completed':
            print('Snapshot complete! Dataset is now archived')
