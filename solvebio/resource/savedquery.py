from ..query import Query

from .dataset import Dataset

from .apiresource import CreateableAPIResource
from .apiresource import ListableAPIResource
from .apiresource import UpdateableAPIResource
from .apiresource import DeletableAPIResource


class SavedQuery(CreateableAPIResource, ListableAPIResource,
                 UpdateableAPIResource, DeletableAPIResource):
    """
    SavedQuery contain the schema of a Dataset, including some
    properties and all the fields.
    """
    RESOURCE_VERSION = 2

    LIST_FIELDS = (
        ('id', 'ID'),
        ('name', 'Name'),
        ('description', 'Description'),
    )

    def query(self, dataset=None):
        if 'id' not in self or not self['id']:
            raise Exception(
                'No SavedQuery ID was provided. '
                'Please instantiate the SavedQuery '
                'object with an ID.')
        if not dataset:
            raise Exception(
                'No Dataset was specified. '
                'Please provide either the Dataset object or '
                'the Dataset ID.')

        if isinstance(dataset, Dataset):
            dataset_id = dataset.id
        else:
            dataset_id = dataset

        return Query(dataset_id, client=self._client, **self.params)
