from .apiresource import CreateableAPIResource
from .apiresource import ListableAPIResource
from .apiresource import UpdateableAPIResource
from .apiresource import DeletableAPIResource


class Beacon(CreateableAPIResource,
             ListableAPIResource,
             DeletableAPIResource,
             UpdateableAPIResource):
    """
    Beacons provide entity-based search endpoints for datasets. Beacons
    must be created within Beacon Sets.
    """
    RESOURCE_VERSION = 2

    LIST_FIELDS = (
        ('id', 'ID'),
        ('title', 'Title'),
        ('description', 'Description'),
        ('vault_object_id', 'Object ID'),
    )

    def _query_url(self):
        if 'query_url' not in self:
            if 'id' not in self or not self['id']:
                raise Exception(
                    'No Beacon ID was provided. '
                    'Please instantiate the Beacon'
                    'object with an ID.')
            return self.instance_url() + '/query'
        return self['query_url']

    def query(self, query, entity_type=None):
        data = {
            'query': query,
            'entity_type': entity_type
        }
        return self._client.post(self._query_url(), data)
