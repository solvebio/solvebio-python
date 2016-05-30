from __future__ import absolute_import

from .apiresource import DeletableAPIResource
from .apiresource import DownloadableAPIResource
from .apiresource import ListableAPIResource
from .solveobject import convert_to_solve_object
from ..client import client
from ..client import requests
from ..utils.md5sum import md5sum

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
        Uses direct-to-S3 uploads:

        1) Creates an Upload placeholder on the API to get a PUT URL
        2) Uploads the file to S3 (S3 verifies the MD5)
        """
        # Ensure the file exists, get MD5, mimetype, size.
        path = os.path.expanduser(path)
        if not os.path.exists(path):
            raise Exception('File not found: {}'.format(path))

        # Calculate MD5 without multipart chunking.
        md5, _ = md5sum(path, multipart_threshold=None)
        params = {
            'filename': os.path.basename(path),
            'mimetype': 'application/octet-stream',
            'size': os.path.getsize(path),
            'md5': md5
        }

        response = client.post(cls.class_url(), params)
        upload = convert_to_solve_object(response)

        # Upload to S3
        with open(path, 'rb') as data:
            headers = {
                'Content-MD5': upload.base64_md5,
                'Content-Type': upload.mimetype,
                'Content-Length': str(upload.size)
            }
            requests.put(
                upload.s3_upload_url,
                data=data,
                headers=headers)

        return upload
