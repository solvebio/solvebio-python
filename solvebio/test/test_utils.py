from __future__ import absolute_import
import os

from .helper import SolveBioTestCase
from solvebio.utils.files import check_gzip_path


class GzipTest(SolveBioTestCase):

    def test_gzip_file(self):
        path = os.path.join(os.path.dirname(__file__), "data")
        for yes_gzip in ['some_export.json.gz',
                         'sample.vcf.gz']:
            path = os.path.join(path, yes_gzip)
            self.assertTrue(check_gzip_path(path), path)

        for non_gzip in ['sample2.vcf',
                         'test_export.json',
                         'test_export.csv',
                         'test_export.xlsx']:
            path = os.path.join(path, non_gzip)
            self.assertFalse(check_gzip_path(path), path)
