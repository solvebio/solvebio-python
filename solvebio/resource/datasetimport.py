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
        print("Waiting for import (id = {0}) to start...".format(self.id))
        print("View your import status on MESH: "
              "https://my.solvebio.com/jobs/imports/{0}"
              .format(self.id))

        import_status = self.status

        while self.status in ['queued', 'running']:
            if self.status == 'running':
                for commit in self.dataset_commits:
                    if not commit.is_approved:
                        print("One or more commits need admin approval.")
                        print("Visit the following page to approve them: "
                              "https://my.solvebio.com/jobs/imports/{0}"
                              .format(self.id))
                        # Nothing we can do here!
                        return

                    print("Commit '{0}' is {1}: {2}/{3} records indexed"
                          .format(commit.title,
                                  commit.status,
                                  commit.records_modified,
                                  commit.records_total))

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

        if self.status == 'completed':
            print("View your imported data: "
                  "https://my.solvebio.com/data/{0}"
                  .format(self['dataset']['full_name']))
