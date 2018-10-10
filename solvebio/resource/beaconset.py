from .apiresource import CreateableAPIResource
from .apiresource import ListableAPIResource
from .apiresource import UpdateableAPIResource
from .apiresource import DeletableAPIResource


class BeaconSet(CreateableAPIResource,
                ListableAPIResource,
                DeletableAPIResource,
                UpdateableAPIResource):
    """
    A beacon set is an arbitrary group of beacons, which provide
    entity-based search endpoints for datasets. Beacon sets can be
    used to query a group of related datasets in a single API request.
    """
    RESOURCE_VERSION = 2

    LIST_FIELDS = (
        ('id', 'ID'),
        ('title', 'Title'),
        ('description', 'Description'),
        ('is_shared', 'Shared?'),
        ('is_public', 'Public?'),
        ('created_at', 'Created'),
        ('updated_at', 'Last Updated'),
    )

    def _query_url(self):
        if 'query_url' not in self:
            if 'id' not in self or not self['id']:
                raise Exception(
                    'No BeaconSet ID was provided. '
                    'Please instantiate the BeaconSet'
                    'object with an ID.')
            return self.instance_url() + '/query'
        return self['query_url']

    def query(self, query, entity_type=None):
        data = {
            'query': query,
            'entity_type': entity_type
        }
        return self._client.post(self._query_url(), data)
