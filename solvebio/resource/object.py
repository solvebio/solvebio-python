"""Solvebio Object API resource"""
from solvebio.errors import NotFoundError

from ..client import client

from .solveobject import convert_to_solve_object
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
    RESOURCE_VERSION = 2

    LIST_FIELDS = (
        ('id', 'ID'),
        ('vault_id', 'Vault ID'),
        ('vault_name', 'Vault Name'),
        ('object_type', 'Object Type'),
        ('path', 'Path'),
        ('filename', 'Filename'),
        ('description', 'Description'),
    )

    @classmethod
    def get_by_full_path(cls, full_path, **params):
        _params = {'full_path': full_path}
        _params.update(params)
        return cls._retrieve_helper(_params, 'full_path', **params)

    @classmethod
    def get_by_path(cls, path, **params):
        _params = {'path': path}
        _params.update(params)
        return cls._retrieve_helper(_params, 'path', **params)

    @classmethod
    def _retrieve_helper(cls, filter_, name, **params):
        params.update(filter_)
        url = cls.class_url()
        response = client.get(url, params)
        results = convert_to_solve_object(response)
        objects = results.data
        allow_multiple = params.pop('allow_multiple', None)

        if len(objects) > 1:
            if allow_multiple:
                return objects
            else:
                raise Exception('Multiple objects found with {0} {1}'
                                .format(name, filter_[name]))
        elif len(objects) == 1:
            return objects[0]
        else:
            raise NotFoundError('Object not found with {0} {1}'
                                .format(name, filter_[name]))
