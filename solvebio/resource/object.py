"""Solvebio Depository API resource"""
from ..help import open_help

from .apiresource import CreateableAPIResource
from .apiresource import ListableAPIResource
from .apiresource import SearchableAPIResource
from .apiresource import UpdateableAPIResource
from .apiresource import DeletableAPIResource


class Object(CreateableAPIResource,
             ListableAPIResource,
             DeletableAPIResource,
             SearchableAPIResource,
             UpdateableAPIResource):
    """
    An object is a resource in a Vault.  It has three possible types,
    though more may be added later: folder, file, and SolveBio Dataset.
    """
    LIST_FIELDS = (
        ('id', 'ID'),
        ('description', 'Description')
    )
    USES_V2_ENDPOINT = True


    def help(self):
        # TODO: add a help file?
        open_help('/library/{0}'.format(self['full_name']))