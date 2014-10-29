from test_helper import unittest
import tempfile
import os
import solvebio

from solvebio.resource import Annotation
from solvebio.errors import SolveError

import hashlib


def md5_file(fileobj, blocksize=65535):
    hasher = hashlib.md5()
    fileobj.seek(0)
    buf = fileobj.read(blocksize)

    while len(buf) > 0:
        hasher.update(buf)
        buf = fileobj.read(blocksize)

    return hasher.hexdigest()


class AnnotationAccessTest(unittest.TestCase):

    def test_annotation(self):
        self.assertEqual(Annotation.class_url(), '/v1/annotations',
                         'Annotation.class_url()')

    def test_annotation_download(self):
        all = Annotation.all()
        if all.total == 0:
            return unittest.skip("no annotations found to download")
        ann = all.data[0]
        try:
            response = ann.download(tempfile.gettempdir())
            self.assertEqual(response.status_code, 200,
                             "Download annotation file status ok")
            self.assertTrue(os.path.exists(response.filename),
                            "Download annotation file on filesystem")
            vcf_md5 = md5_file(open(response.filename, 'rb'))
            if solvebio.api_key == '0cedb161d845e6a58ec6781478b8314c536e632f':
                self.assertEqual(vcf_md5, 'e5ae61b8c6f334195d954423d1072ac1',
                                 "vcf_mdf on download")
            else:
                unittest.skip('MD5 test only works with test user')
            os.remove(response.filename)
        except SolveError as err:
            self.assertEqual(err.status_code, 404)


if __name__ == "__main__":
    unittest.main()
