"""Solvebio Dataset API Resource"""
from ..client import client
from ..help import open_help
from ..query import Query

from .solveobject import convert_to_solve_object
from .apiresource import CreateableAPIResource, ListableAPIResource, \
    UpdateableAPIResource
from .datasetfield import DatasetField


class Dataset(CreateableAPIResource, ListableAPIResource,
              UpdateableAPIResource):
    """
    Datasets are access points to data. Dataset names are unique
    within versions of a depository.
    """
    LIST_FIELDS = (
        ('full_name', 'Name'),
        ('depository', 'Depository'),
        ('title', 'Title'),
        ('description', 'Description'),
    )

    def depository_version(self):
        from .depositoryversion import DepositoryVersion
        return DepositoryVersion.retrieve(self['depository_version'])

    def depository(self):
        from .depository import Depository
        return Depository.retrieve(self['depository'])

    def fields(self, name=None, **params):
        if 'fields_url' not in self:
            raise Exception(
                'Please use Dataset.retrieve({ID}) before doing looking '
                'up fields')

        if name:
            # construct the field's full_name if a field name is provided
            return DatasetField.retrieve(
                '/'.join([self['full_name'], name]))

        response = client.get(self.fields_url, params)
        results = convert_to_solve_object(response)
        results.set_tabulate(
            ['name', 'data_type', 'description'],
            headers=['Field', 'Data Type', 'Description'],
            aligns=['left', 'left', 'left'], sort=True)

        return results

    def _data_url(self):
        if 'data_url' not in self:
            if 'id' not in self or not self['id']:
                raise Exception(
                    'No Dataset ID was provided. '
                    'Please instantiate the Dataset '
                    'object with an ID or full_name.')
            # automatically construct the data_url from the ID
            return self.instance_url() + u'/data'
        return self['data_url']

    def query(self, **params):
        self._data_url()  # raises an exception if there's no ID
        return Query(self['id'], **params)

    def help(self):
        open_help('/library/{0}'.format(self['full_name']))
