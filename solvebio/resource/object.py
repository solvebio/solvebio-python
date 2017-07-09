"""Solvebio Object API resource"""
from ..help import open_help
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
    LIST_FIELDS = (
        ('id', 'ID'),
        ('description', 'Description'),
        ('path', 'Path'),
        ('filename', 'Filename'),
        ('filename', 'Filename'),

    )
    USES_V2_ENDPOINT = True

    @classmethod
    def retrieve_by_full_path(cls, full_path, **params):
        # TODO - arg needs quoting?
        params.update({'full_path': full_path})
        url = cls.class_url()
        response = client.get(url, params)
        results = convert_to_solve_object(response)
        objects = results.data

        if len(objects) > 1:
            if params.get('allow_multiple'):
                return objects
            else:
                pass
                # TODO - raise exception
        elif len(objects) == 1:
            return objects[0]
        else:
            pass
            # TODO - raise exception - no results

    def help(self):
        # TODO: add a help file?
        open_help('/library/{0}'.format(self['full_name']))
