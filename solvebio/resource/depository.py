"""Solvebio Depository API resource"""
from ..client import client
from ..help import open_help

from .solveobject import convert_to_solve_object
from .apiresource import CreateableAPIResource, ListableAPIResource, \
    SearchableAPIResource, UpdateableAPIResource
from .depositoryversion import DepositoryVersion


class Depository(CreateableAPIResource, ListableAPIResource,
                 SearchableAPIResource, UpdateableAPIResource):
    """
    A depository (or data repository) is like a source code
    repository, but for datasets. Depositories have one or more
    versions, which in turn contain one or more datasets. Typically,
    depositories contain a series of datasets that are compatible with
    each other (i.e. they come from the same data source or project).
    """
    # Fields that get shown by tabulate
    TAB_FIELDS = ['description', 'full_name', 'latest_version', 'name',
                  'title', 'url']

    def versions(self, name=None, **params):
        if name:
            # construct the depo version full name
            return DepositoryVersion.retrieve(
                '/'.join([self['full_name'], name]))

        response = client.get(self.versions_url, params)
        results = convert_to_solve_object(response)
        results.tabulate(
            ['full_name', 'title', 'description'],
            headers=['Depository Version', 'Title', 'Description'],
            aligns=['left', 'left', 'left'], sort=True)

        return results

    def help(self):
        open_help(self['full_name'])
