from __future__ import absolute_import

from .apiresource import DeletableAPIResource
from .apiresource import DownloadableAPIResource
from .apiresource import ListableAPIResource
from .solveobject import convert_to_solve_object
from ..client import client

import os


class Upload(DeletableAPIResource, DownloadableAPIResource,
             ListableAPIResource):
    """
    An Upload represents any VCF or JSON file uploaded to SolveBio.
    SolveBio supports files with the following extensions:

    * .vcf
    * .vcf.gz
    * .json
    * .json.gz

    Any other extension will be rejected.

    SolveBio supports VCF version 4.0 to 4.2. JSON files should
    contain individual JSON records, one per line.
    """

    @classmethod
    def create(cls, path, **params):
        """
        Uploads a local file at the specified path.
        """
        # TODO: If the file is larger than 50mb, use the direct S3
        #       upload method.
        files = {
            'file': open(os.path.expanduser(path), 'rb')
        }
        response = client.post(cls.class_url(), params, files=files)
        return convert_to_solve_object(response)
