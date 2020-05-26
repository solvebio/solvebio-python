"""Solvebio DatasetField API Resource"""
from .solveobject import convert_to_solve_object
from .apiresource import CreateableAPIResource
from .apiresource import ListableAPIResource
from .apiresource import UpdateableAPIResource
from .apiresource import DeletableAPIResource

from ..annotate import Expression


class DatasetField(CreateableAPIResource,
                   ListableAPIResource,
                   DeletableAPIResource,
                   UpdateableAPIResource):
    """
    Each SolveBio dataset has a different set of fields, some of
    which can be used as filters. Dataset field resources provide
    users with documentation about each field.
    """
    RESOURCE = '/v2/dataset_fields'

    def facets(self, **params):
        response = self._client.get(self.facets_url, params)
        return convert_to_solve_object(response, client=self._client)

    def help(self):
        return self.facets()

    def evaluate(self):
        if not self.get('expression'):
            return None

        return Expression(self['expression'], client=self._client).evaluate(
            data_type=self.get('data_type', 'string'))
