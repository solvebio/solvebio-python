"""Solvebio DatasetField API Resource"""
import re

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
    ALLOW_FULL_NAME_ID = True
    FULL_NAME_REGEX = r'^([\w\d\-\.]+/){3}[\w\d\-\.]+$'

    @classmethod
    def retrieve(cls, id, **params):
        """Supports lookup by ID or full name"""
        if isinstance(id, unicode) or isinstance(id, str):
            _id = unicode(id).strip()
            id = None
            if re.match(cls.FULL_NAME_REGEX, _id):
                params.update({'full_name': _id})
            else:
                raise Exception('Unrecognized full name.')

        return super(DatasetField, cls).retrieve(id, **params)

    def facets(self, **params):
        response = client.get(self.facets_url, params)
        return convert_to_solve_object(response)

    def help(self):
        return self.facets()
