"""Solvebio Depository API resource"""
# from ..client import client
from ..help import open_help

# from .solveobject import convert_to_solve_object
from .apiresource import CreateableAPIResource
from .apiresource import ListableAPIResource
from .apiresource import SearchableAPIResource
from .apiresource import UpdateableAPIResource
from .apiresource import DeletableAPIResource


class Vault(CreateableAPIResource,
            ListableAPIResource,
            DeletableAPIResource,
            SearchableAPIResource,
            UpdateableAPIResource):
    """
    A vault is like a filesystem that can contain files, folder,
    and SolveBio datasets.  Vaults can be "connected" to external resources
    such as DNAnexus and SevenBridges projects, or Amazon S3 Buckets.
    Typically, vaults contain a series of datasets that are compatible with
    each other (i.e. they come from the same data source or project).
    """
    USES_V2_ENDPOINT = True

    LIST_FIELDS = (
        ('id', 'ID'),
        ('description', 'Description')
    )

    def datasets(self, name=None, **params):
        pass
        # if name:
        #     # construct the dataset full name
        #     return Dataset.retrieve(
        #         '/'.join([self['full_name'], name]))
        #
        # response = client.get(self.datasets_url, params)
        # results = convert_to_solve_object(response)
        # results.set_tabulate(
        #     ['full_name', 'title', 'description'],
        #     headers=['Dataset', 'Title', 'Description'],
        #     aligns=['left', 'left', 'left'], sort=True)
        #
        # return results


    def objects(self, name=None, **params):
        pass
        # if name:
        #     # construct the dataset full name
        #     return Dataset.retrieve(
        #         '/'.join([self['full_name'], name]))
        #
        # response = client.get(self.datasets_url, params)
        # results = convert_to_solve_object(response)
        # results.set_tabulate(
        #     ['full_name', 'title', 'description'],
        #     headers=['Dataset', 'Title', 'Description'],
        #     aligns=['left', 'left', 'left'], sort=True)
        #
        # return results


    # def versions(self, name=None, **params):
    #     if name:
    #         # construct the depo version full name
    #         return DepositoryVersion.retrieve(
    #             '/'.join([self['full_name'], name]))
    #
    #     response = client.get(self.versions_url, params)
    #     results = convert_to_solve_object(response)
    #     results.set_tabulate(
    #         ['full_name', 'title', 'description'],
    #         headers=['Depository Version', 'Title', 'Description'],
    #         aligns=['left', 'left', 'left'], sort=True)
    #
    #     return results
    #
    # def latest_version(self):
    #     return self.versions(self['latest_version'].split('/')[-1])

    def help(self):
        # TODO: add a help file?
        open_help('/library/{0}'.format(self['full_name']))