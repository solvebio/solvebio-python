from .apiresource import CreateableAPIResource
from .apiresource import ListableAPIResource
from .apiresource import UpdateableAPIResource
from .apiresource import DeletableAPIResource


class DatasetTemplate(CreateableAPIResource, ListableAPIResource,
                      UpdateableAPIResource, DeletableAPIResource):
    """
    DatasetTemplates contain the schema of a Dataset, including some
    properties and all the fields.
    """
    USES_V2_ENDPOINT = True

    LIST_FIELDS = (
        ('id', 'ID'),
        ('name', 'Name'),
        ('version', 'Version'),
        ('description', 'Description'),
    )
