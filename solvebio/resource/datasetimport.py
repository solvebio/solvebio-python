from .apiresource import ListableAPIResource
from .apiresource import DeletableAPIResource
from .apiresource import CreateableAPIResource
from .apiresource import UpdateableAPIResource
from .solveobject import convert_to_solve_object

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

    def follow(self, loop=True):

        if self.status == 'queued':
            print("Waiting for import (id = {0}) to start..."
                  .format(self.id))

        import_status = self.status
        while self.status in ['queued', 'running']:
            time.sleep(3)
            self.refresh()
            if self.status != import_status:
                print("Import is now {0} (was {1})"
                      .format(self.status, import_status))
                import_status = self.status
                # When status changes to running, indicate
                # pre-processing step.
                if self.status == 'running':
                    print("Processing and validating file(s), "
                          "this may take a few minutes...")

            if not loop:
                print("Import {0} is {1}"
                      .format(self.id, self.status))
                return

        if self.status == 'failed':
            print("Import processing and validation failed.")
            print("Reason: {}".format(self.error_message))
            return

        if self.status == 'canceled':
            print("Import processing and validation was canceled")
            print("Reason: {}".format(self.error_message))
            return

        print("Validation completed. Beginning indexing of commits.")

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

        print("View your imported data: "
              "https://my.solvebio.com/data/{0}"
              .format(self['dataset']['id']))
