"""Solvebio DatasetField API Resource"""
from ..client import client

from .solveobject import convert_to_solve_object
from .apiresource import CreateableAPIResource, ListableAPIResource, \
    UpdateableAPIResource


class DatasetField(CreateableAPIResource, ListableAPIResource,
                   UpdateableAPIResource):
    """
    Each SolveBio dataset has a different set of fields, some of
    which can be used as filters. Dataset field resources provide
    users with documentation about each field.
    """
    def facets(self, **params):
        response = client.get(self.facets_url, params)
        return convert_to_solve_object(response)

    def help(self):
        return self.facets()
