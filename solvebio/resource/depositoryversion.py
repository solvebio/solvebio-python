"""Solvebio DepositoryVersion Resource"""
from ..client import client
from ..help import open_help

from .solveobject import convert_to_solve_object
from .apiresource import CreateableAPIResource, ListableAPIResource, \
    UpdateableAPIResource
from .dataset import Dataset


class DepositoryVersion(CreateableAPIResource, ListableAPIResource,
                        UpdateableAPIResource):

    """
    Depositories and datasets may be updated
    periodically. Depository versions are a mechanism to keep track of
    changes within a depository. Depository versions are named
    according to the Semantic Versioning guidelines. Example version
    names include: 1.0.0 and 0.0.1-beta.

    For a given version MAJOR.MINOR.PATCH-EXTENSION:

    MAJOR denotes backwards-incompatible changes to dataset schemas,
    or massive new releases within a depository, MINOR denotes
    backwards-compatible changes within a depository, and PATCH changes
    when minor, backwards-compatible changes are made within a depository.
    EXTENSION labels pre-release and build metadata.
    """
    # Fields that get shown by tabulate
    TAB_FIELDS = ['datasets_url', 'depository', 'description', 'full_name',
                  'latest', 'url']

    def datasets(self, name=None, **params):
        if name:
            # construct the dataset full name
            return Dataset.retrieve(
                '/'.join([self['full_name'], name]))

        response = client.get(self.datasets_url, params)
        results = convert_to_solve_object(response)
        results.tabulate(
            ['full_name', 'title', 'description'],
            headers=['Dataset', 'Title', 'Description'],
            aligns=['left', 'left', 'left'], sort=True)

        return results

    def help(self):
        open_help(self['full_name'])
