"""Depository and DepositoryVersion Classes"""

from resource import CreateableAPIResource, ListableAPIResource, \
     SearchableAPIResource, UpdateableAPIResource
from solveobject import convert_to_solve_object

class Depository(CreateableAPIResource, ListableAPIResource,
                 SearchableAPIResource, UpdateableAPIResource):
    ALLOW_FULL_NAME_ID = True
    FULL_NAME_REGEX = r'^[\w\d\-\.]+$'

    @classmethod
    def retrieve(cls, id, **params):
        """Supports lookup by ID or full name"""
        if isinstance(id, unicode) or isinstance(id, str):
            _id = unicode(id).strip()
            id = None
            if re.match(cls.FULL_NAME_REGEX, _id):
                params.update({'full_name': _id})
            else:
                raise Exception('Unrecognized full name: "%s"' % _id)

        return super(Depository, cls).retrieve(id, **params)

    def versions(self, name=None, **params):
        if name:
            # construct the depo version full name
            return DepositoryVersion.retrieve(
                '/'.join([self['full_name'], name]))

        response = client.request('get', self.versions_url, params)
        return convert_to_solve_object(response)

    def help(self):
        open_help(self['full_name'])


class DepositoryVersion(CreateableAPIResource, ListableAPIResource,
                        UpdateableAPIResource):
    ALLOW_FULL_NAME_ID = True
    FULL_NAME_REGEX = r'^[\w\d\-\.]+/[\w\d\-\.]+$'

    @classmethod
    def retrieve(cls, id, **params):
        """Supports lookup by full name"""
        if isinstance(id, unicode) or isinstance(id, str):
            _id = unicode(id).strip()
            id = None
            if re.match(cls.FULL_NAME_REGEX, _id):
                params.update({'full_name': _id})
            else:
                raise Exception('Unrecognized full name.')

        return super(DepositoryVersion, cls).retrieve(id, **params)

    def datasets(self, name=None, **params):
        if name:
            # construct the dataset full name
            return Dataset.retrieve(
                '/'.join([self['full_name'], name]))

        response = client.request('get', self.datasets_url, params)
        return convert_to_solve_object(response)

    def help(self):
        open_help(self['full_name'])

    def release(self, released_at=None):
        """Set the released flag and optional release date and save"""
        if released_at:
            self.released_at = released_at
        self.released = True
        self.save()

    def unrelease(self):
        """Unset the released flag and save"""
        self.released = False
        self.save()
