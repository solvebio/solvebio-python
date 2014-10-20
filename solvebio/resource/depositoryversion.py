"""Solvebio DepositoryVersion Resource"""
import re

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

    ALLOW_FULL_NAME_ID = True
    FULL_NAME_REGEX = r'^[\w\d\-\.]+/[\w\d\-\.]+$'

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

        return super(DepositoryVersion, cls).retrieve(id, **params)

    def datasets(self, name=None, **params):
        if name:
            # construct the dataset full name
            return Dataset.retrieve(
                '/'.join([self['full_name'], name]))

        response = client.request('get', self.datasets_url, params)
        return convert_to_solve_object(response)

    def help(self):
        open_help(self['full_name'])

    def release(self, released_at=None):
        """Set the released flag and optional release date and save"""
        if released_at:
            self.released_at = released_at
        self.released = True
        self.save()

    def unrelease(self):
        """Unset the released flag and save"""
        self.released = False
        self.save()
