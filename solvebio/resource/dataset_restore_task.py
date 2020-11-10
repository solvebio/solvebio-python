from .apiresource import ListableAPIResource
from .apiresource import CreateableAPIResource
from .solveobject import convert_to_solve_object

import time


class DatasetRestoreTask(CreateableAPIResource, ListableAPIResource):
    """
    DatasetRestoreTask represents the task to restore an archived dataset
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
            print("Waiting for Dataset Restore task (id = {0}) to start..."
                  .format(self.id))

        status = self.status
        while self.status in ['queued', 'running']:
            if self.status != status:
                print("Restore is now {0} (was {1})"
                      .format(self.status, status))
                status = self.status

            if self.status == 'running':
                print("Restore '{0}' is {1}".format(self.id, self.status))

            if not loop:
                return

            time.sleep(3)
            self.refresh()

        if self.status == 'completed':
            print('Restore complete! Dataset is now avaiable')
