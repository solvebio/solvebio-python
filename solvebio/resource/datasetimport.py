from .apiresource import ListableAPIResource
from .apiresource import DeletableAPIResource
from .apiresource import CreateableAPIResource
from .apiresource import UpdateableAPIResource
from .solveobject import convert_to_solve_object
from .task import Task
from .datasetcommit import follow_commits

import time


class DatasetImport(CreateableAPIResource, ListableAPIResource,
                    UpdateableAPIResource, DeletableAPIResource):
    """
    DatasetImports represent an import task that takes
    either an object_id or a file manifest (list of file URLs)
    and converts them to a SolveBio-compatible format which can
    then be indexed by a dataset.

    For interactive use, DatasetImport can be "followed" to watch
    the progression of an import job.
    """
    RESOURCE_VERSION = 2

    LIST_FIELDS = (
        ('id', 'ID'),
        ('title', 'Title'),
        ('description', 'Description'),
        ('status', 'Status'),
        ('created_at', 'Created'),
    )

    @property
    def dataset(self):
        return convert_to_solve_object(self['dataset'], client=self._client)

    def follow(self, loop=True, sleep_seconds=Task.SLEEP_WAIT_DEFAULT):

        if self.status == 'queued':
            print("Waiting for import (id = {0}) to start..."
                  .format(self.id))

        import_status = self.status
        while self.status in ['queued', 'running']:

            if self.status != import_status:
                print("Import is now {0} (was {1})"
                      .format(self.status, import_status))
                import_status = self.status
                # When status changes to running, indicate
                # pre-processing step.
                if self.status == 'running':
                    print("Processing and validating file(s), "
                          "this may take a few minutes...")
            elif self.status == 'running':
                records_count = self.metadata.get("progress", {}) \
                    .get("processed_records", 0)
                print("Import {0} is {1}: {2} records processed".format(
                    self.id, self.status, records_count))
            else:
                print("Import {0} is {1}".format(self.id, self.status))

            if not loop:
                return

            time.sleep(sleep_seconds)
            self.refresh()

        if self.status == 'failed':
            print("Import processing and validation failed.")
            print("Reason: {}".format(self.error_message))
            return

        if self.status == 'canceled':
            print("Import processing and validation was canceled")
            print("Reason: {}".format(self.error_message))
            return

        # Follow commits until complete
        follow_commits(self, sleep_seconds)

        print("View your imported data: "
              "https://my.solvebio.com/data/{0}"
              .format(self['dataset']['id']))
