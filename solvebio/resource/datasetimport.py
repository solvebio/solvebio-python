from .apiresource import CreateableAPIResource
from .apiresource import ListableAPIResource
from .apiresource import UpdateableAPIResource
from .apiresource import DeletableAPIResource

import time


class DatasetImport(CreateableAPIResource, ListableAPIResource,
                    UpdateableAPIResource, DeletableAPIResource):
    """
    DatasetImports represent an import task that takes
    either an uploaded file or file manifest (list of file URLs)
    and converts them to a SolveBio-compatible format which can
    then be indexed by a dataset.

    For interactive use, DatasetImport can be "followed" to watch
    the progression of an import job.
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
        print("View your import status on MESH: "
              "https://my.solvebio.com/jobs/imports/{0}"
              .format(self.id))

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

        if self.status == 'failed':
            print("Import processing and validation failed.")
            print("Reason: {}".format(self.error_message))
            return

        if self.status == 'canceled':
            print("Import processing and validation was canceled")
            print("Reason: {}".format(self.error_message))
            return

        print("Validation completed. Beginning indexing of commits.")
        unapproved_commits = [c for c in self.dataset_commits
                              if not c.is_approved]
        if unapproved_commits:
            # Nothing we can do here!
            print("One or more commits need admin approval.")
            print("Visit the following page to approve them: "
                  "https://my.solvebio.com/jobs/imports/{0}"
                  .format(self.id))

        # follow approved, unfinished commits
        while True:
            approved_commits = [
                c for c in self.dataset_commits if c.is_approved
            ]

            unfinished_commits = [
                c for c in approved_commits
                if c.status in ['queued', 'running']
            ]

            if not unfinished_commits:
                print("All commits have finished processing")
                break

            if len(approved_commits) > 1:
                print("{0}/{1} approved commits have finished processing"
                      .format(len(approved_commits) - len(unfinished_commits),
                              len(approved_commits)))

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
              .format(self['dataset']['full_name']))
