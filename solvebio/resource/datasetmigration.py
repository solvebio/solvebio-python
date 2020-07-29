from .apiresource import ListableAPIResource
from .apiresource import DeletableAPIResource
from .apiresource import CreateableAPIResource
from .solveobject import convert_to_solve_object
from .task import Task
from .datasetcommit import follow_commits

import time


class DatasetMigration(CreateableAPIResource, ListableAPIResource,
                       DeletableAPIResource):
    """
    DatasetMigration represent an task that copies data between
    two Datasets or modifies data within a single Dataset.

    For interactive use, DatasetMigration can be "followed" to watch
    the progression of the task.
    """
    RESOURCE_VERSION = 2

    LIST_FIELDS = (
        ('id', 'ID'),
        ('status', 'Status'),
        ('source', 'Source'),
        ('target', 'Target'),
        ('documents_count', 'Records'),
        ('created_at', 'Created'),
        ('updated_at', 'Updated'),
    )

    @property
    def source(self):
        response = self._client.get(self['source']['url'], {})
        return convert_to_solve_object(response, client=self._client)

    @property
    def target(self):
        response = self._client.get(self['target']['url'], {})
        return convert_to_solve_object(response, client=self._client)

    def follow(self, loop=True, sleep_seconds=Task.SLEEP_WAIT_DEFAULT):
        _status = self.status
        if self.status == 'queued':
            print("Waiting for migration (id = {0}) to start..."
                  .format(self.id))

        while self.status in ['queued', 'running']:
            if self.status != _status:
                print("Migration is now {0} (was {1})"
                      .format(self.status, _status))
                _status = self.status

            if self.status == 'running':
                processed_records = self.metadata\
                    .get('progress', {})\
                    .get('processed_records', 0)
                print("Migration '{0}' is {1}: {2}/{3} records migrated"
                      .format(self.id,
                              self.status,
                              processed_records,
                              self.documents_count))

            if not loop:
                return

            time.sleep(sleep_seconds)
            self.refresh()

        if self.status == 'failed':
            print("Migration failed.")
            print("Reason: {}".format(self.error_message))
            return

        if self.status == 'canceled':
            print("Migration was canceled")
            print("Reason: {}".format(self.error_message))
            return

        # Follow commits until complete
        follow_commits(self, sleep_seconds)

        print("View your migrated data: "
              "https://my.solvebio.com/data/{0}"
              .format(self['target']['id']))
