"""Solvebio Dataset API Resource"""
import re

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
    ALLOW_FULL_NAME_ID = True
    FULL_NAME_REGEX = r'^([\w\d\-\.]+/){2}[\w\d\-\.]+$'

    @classmethod
    def retrieve(cls, id, **params):
        """Supports lookup by full name"""
        if isinstance(id, unicode) or isinstance(id, str):
            _id = unicode(id).strip()
            id = None
            if re.match(cls.FULL_NAME_REGEX, _id):
                params.update({'full_name': _id})
            else:
                raise Exception('Unrecognized full name.')

        return super(Dataset, cls).retrieve(id, **params)

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
        results.tabulate(
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
        q = Query(self['id'], **params)
        return q.filter(params.get('filters')) if params.get('filters') else q

    def help(self):
        open_help(self['full_name'])
