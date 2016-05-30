from .apiresource import CreateableAPIResource, ListableAPIResource, \
    UpdateableAPIResource


class DatasetTemplate(CreateableAPIResource, ListableAPIResource,
                      UpdateableAPIResource):
    """
    DatasetTemplates contain the schema of a Dataset, including some
    properties and all the fields.
    """
    LIST_FIELDS = (
        ('id', 'ID'),
        ('name', 'Name'),
        ('version', 'Version'),
        ('description', 'Description'),
    )
