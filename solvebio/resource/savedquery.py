from .apiresource import CreateableAPIResource
from .apiresource import ListableAPIResource
from .apiresource import UpdateableAPIResource
from .apiresource import DeletableAPIResource


class SavedQuery(CreateableAPIResource, ListableAPIResource,
                 UpdateableAPIResource, DeletableAPIResource):
    """
    SavedQuery contain the schema of a Dataset, including some
    properties and all the fields.
    """
    RESOURCE_VERSION = 2

    LIST_FIELDS = (
        ('id', 'ID'),
        ('name', 'Name'),
        ('description', 'Description'),
    )
