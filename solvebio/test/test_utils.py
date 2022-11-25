from __future__ import absolute_import
import os

from .helper import SolveBioTestCase
from unittest import TestCase
from solvebio.utils.files import check_gzip_path, separate_filename_extension

FILENAME_PARAMS = [
    {
        "filename": "test.txt",
        "base": "test",
        "ext": ".txt",
        "compression": ""
    },
    {
        "filename": "/path/to/test.txt",
        "base": "/path/to/test",
        "ext": ".txt",
        "compression": ""
    },
    {
        "filename": "test.txt.gz",
        "base": "test",
        "ext": ".txt",
        "compression": ".gz"
    },
]


class FilenameTests(SolveBioTestCase, TestCase):

    def test_extract_filename(self):
        for params in FILENAME_PARAMS:
            base, ext, compression = separate_filename_extension(params['filename'])
            self.assertEqual(base, params['base'])
            self.assertEqual(ext, params['ext'])
            self.assertEqual(compression, params['compression'])


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
