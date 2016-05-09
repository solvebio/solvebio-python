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
