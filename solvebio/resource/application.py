"""Solvebio Application API Resource"""
from .apiresource import CreateableAPIResource
from .apiresource import ListableAPIResource
from .apiresource import SearchableAPIResource
from .apiresource import UpdateableAPIResource
from .apiresource import DeletableAPIResource


class Application(CreateableAPIResource,
                  ListableAPIResource,
                  DeletableAPIResource,
                  SearchableAPIResource,
                  UpdateableAPIResource):
    ID_ATTR = 'client_id'
    RESOURCE_VERSION = 2

    LIST_FIELDS = (
        ('client_id', 'Client ID'),
        ('name', 'Name'),
        ('description', 'Description'),
        ('web_url', 'web_url'),
    )
