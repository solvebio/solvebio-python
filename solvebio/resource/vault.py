"""Solvebio Vault API resource"""
# from ..client import client
from ..help import open_help

from .apiresource import CreateableAPIResource
from .apiresource import ListableAPIResource
from .apiresource import SearchableAPIResource
from .apiresource import UpdateableAPIResource
from .apiresource import DeletableAPIResource


class Vault(CreateableAPIResource,
            ListableAPIResource,
            DeletableAPIResource,
            SearchableAPIResource,
            UpdateableAPIResource):
    """
    A vault is like a filesystem that can contain files, folder,
    and SolveBio datasets.  Vaults can be "connected" to external resources
    such as DNAnexus and SevenBridges projects, or Amazon S3 Buckets.
    Typically, vaults contain a series of datasets that are compatible with
    each other (i.e. they come from the same data source or project).
    """
    USES_V2_ENDPOINT = True

    LIST_FIELDS = (
        ('id', 'ID'),
        ('description', 'Description'),
        ('name', 'Name'),
    )

    def datasets(self, name=None, **params):
        pass
        # TODO - add this

    def objects(self, name=None, **params):
        pass
        # TODO - add this

    def help(self):
        # TODO: add a help file?
        open_help('/library/{0}'.format(self['id']))