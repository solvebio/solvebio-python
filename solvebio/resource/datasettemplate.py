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
    RESOURCE_VERSION = 2

    LIST_FIELDS = (
        ('id', 'ID'),
        ('name', 'Name'),
        ('description', 'Description'),
    )

    @property
    def import_params(self):
        """
        Get DatasetImport parameters from a template
        and format them correctly.
        """
        return {
            'target_fields': self.fields,
            'reader_params': self.reader_params,
            'entity_params': self.entity_params,
            'annotator_params': self.annotator_params,
            'validation_params': self.validation_params
        }
