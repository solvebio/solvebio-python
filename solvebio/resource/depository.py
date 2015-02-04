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
    LIST_FIELDS = (
        ('full_name', 'Name'),
        ('title', 'Title'),
        ('description', 'Description')
    )

    def versions(self, name=None, **params):
        if name:
            # construct the depo version full name
            return DepositoryVersion.retrieve(
                '/'.join([self['full_name'], name]))

        response = client.get(self.versions_url, params)
        results = convert_to_solve_object(response)
        results.set_tabulate(
            ['full_name', 'title', 'description'],
            headers=['Depository Version', 'Title', 'Description'],
            aligns=['left', 'left', 'left'], sort=True)

        return results

    def latest_version(self):
        return self.versions(self['latest_version'].split('/')[-1])

    def help(self):
        open_help('/library/{0}'.format(self['full_name']))
