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
    RESOURCE_VERSION = 2

    LIST_FIELDS = (
        ('id', 'ID'),
        ('name', 'Name'),
        ('description', 'Description'),
    )

    @classmethod
    def _list_helper(cls, partial_path, object_type):
        from solvebio import Object

        parts = partial_path.split(':')

        if len(parts) != 2:
            raise Exception('Requires format account:vault_name')

        account_domain, vault_name = parts

        if object_type:
            items = Object.all(object_type=object_type,
                               account_domain=account_domain,
                               name=vault_name)
        else:
            items = Object.all(account_domain=account_domain,
                               name=vault_name)

        return items

    @classmethod
    def files(cls, partial_path):
        return cls._list_helper(partial_path, 'file')

    @classmethod
    def folders(cls, partial_path):
        return cls._list_helper(partial_path, 'folder')

    @classmethod
    def datasets(cls, partial_path):
        return cls._list_helper(partial_path, 'dataset')

    @classmethod
    def objects(cls, partial_path):
        return cls._list_helper(partial_path, None)

    def help(self):
        open_help('/library/{0}'.format(self['id']))
