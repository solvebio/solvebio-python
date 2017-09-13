from .apiresource import CreateableAPIResource
from .apiresource import ListableAPIResource
from .apiresource import DeletableAPIResource

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
    PRINTABLE_NAME = 'dataset migration'

    LIST_FIELDS = (
        ('id', 'ID'),
        ('status', 'Status'),
        ('source', 'Source'),
        ('target', 'Target'),
        ('documents_count', 'Records'),
        ('created_at', 'Created'),
        ('updated_at', 'Updated'),
    )

    def follow(self, loop=True):
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
                print("Migration '{0}' is running: {2}/{3} records completed"
                      .format(self.id,
                              self.status,
                              processed_records,
                              self.documents_count))

            if not loop:
                return

            time.sleep(3)
            self.refresh()

        if self.status == 'completed':
            # Follow unfinished commits
            while True:
                unfinished_commits = [
                    c for c in self.dataset_commits
                    if c.status in ['queued', 'running']
                ]

                if not unfinished_commits:
                    print("All commits have finished processing")
                    break

                if len(unfinished_commits) > 1:
                    print("{0}/{1} commits have finished processing"
                          .format(len(unfinished_commits),
                                  len(self.dataset_commits)))

                # prints a status for each one
                for commit in unfinished_commits:
                    commit.follow(loop=False)

                # sleep
                time.sleep(10)

                # refresh status
                for commit in unfinished_commits:
                    commit.refresh()

            print("View your data: "
                  "https://my.solvebio.com/data/{0}"
                  .format(self['target']))
