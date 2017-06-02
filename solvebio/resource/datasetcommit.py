import time

from .apiresource import CreateableAPIResource
from .apiresource import ListableAPIResource
from .apiresource import UpdateableAPIResource


class DatasetCommit(CreateableAPIResource, ListableAPIResource,
                    UpdateableAPIResource):
    """
    DatasetCommits represent a change made to a Dataset.
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

    def dataset_import(self):
        from .datasetimport import DatasetImport
        return DatasetImport.retrieve(self['dataset_import_id'])

    def follow(self, loop=True):
        if not self.is_approved:
            # Nothing we can do here!
            print("This commit needs admin approval.")
            print("Visit the following page to approve them: "
                  "https://my.solvebio.com/jobs/imports/{0}"
                  .format(self.id))
            return

        print("View your commit status on MESH: "
              "https://my.solvebio.com/jobs/commits/{0}"
              .format(self.id))

        # follow approved, unfinished commits
        while self.status in ['queued', 'running']:
            if self.status == 'running':
                print("Commit '{0}' ({4}) is {1}: {2}/{3} records indexed"
                      .format(self.title,
                              self.status,
                              self.records_modified,
                              self.records_total,
                              self.id))
            else:
                print("Commit '{0}' ({1}) is {2}"
                      .format(self.title,
                              self.id,
                              self.status))

            # When following a parent DatasetImport we do not want to
            # loop for status updates. It will handle its own looping
            # so break out of loop and return here.
            if not loop:
                break

            # sleep
            time.sleep(10)

            # refresh status
            self.refresh()

        if loop:
            print("Commit '{0}' ({1}) is {2}".format(self.title,
                                                     self.id,
                                                     self.status))
            print("View your imported data: "
                  "https://my.solvebio.com/data/{0}"
                  .format(self['dataset']['full_name']))
