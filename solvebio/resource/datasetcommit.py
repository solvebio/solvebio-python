import time

from .apiresource import ListableAPIResource
from .apiresource import CreateableAPIResource
from .apiresource import UpdateableAPIResource
from .solveobject import convert_to_solve_object


class DatasetCommit(CreateableAPIResource, ListableAPIResource,
                    UpdateableAPIResource):
    """
    DatasetCommits represent a change made to a Dataset.
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

    @property
    def parent_object(self):
        """ Get the commit objects parent Import or Migration """
        from . import types
        parent_klass = types.get(self.parent_job_model.split('.')[1])
        return parent_klass.retrieve(self.parent_job_id, client=self._client)

    def follow(self, loop=True):
        # Follow unfinished commits
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
                  .format(self['dataset']['id']))
