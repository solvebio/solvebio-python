from __future__ import absolute_import
import os

from solvebio.resource import Upload
from .helper import SolveBioTestCase


class UploadTest(SolveBioTestCase):
    upload_attrs = [
        ('class_name', 'Upload'),
        ('description', None),
        ('md5', '83acd96171c72ab2bb35e9c52961afd9'),
        ('size', 592),
    ]

    def test_upload_url(self):
        self.assertEqual(Upload.class_url(), '/v1/uploads',
                         'Upload.class_url()')

    def test_create_from_file(self):
        path = os.path.join(os.path.dirname(__file__),
                            "data/sample.vcf.gz")
        upload = Upload.create(path=path)
        self.check_response(upload, self.upload_attrs,
                            'Upload a file')
        self.check_response(Upload.retrieve(upload.id), self.upload_attrs,
                            'Upload.retrieve(id)')
        # Clean up
        expect = [('is_deleted', True), ('id', upload.id)]
        self.check_response(upload.delete(), expect, 'Delete an upload')
