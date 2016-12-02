from __future__ import absolute_import
import hashlib
from solvebio.resource import Dataset
from solvebio import Filter

from .helper import SolveBioTestCase

from os import path, remove
import json


class ExportsTests(SolveBioTestCase):
    """
    Test exporting SolveBio Query object.
    """
    def setUp(self):
        super(ExportsTests, self).setUp()
        filters = Filter(rgd_id='RGD:2645')
        self.dataset = Dataset.retrieve('HGNC/3.0.0-2016-11-10/HGNC')
        self.query = self.dataset.query(filters=filters, fields=['rgd_id'],
                                        genome_build='GRCh37', limit=10)

    # CSVExporter
    def test_csv_exporter(self):
        test_file = '/tmp/test_export.csv'
        reference_file = 'solvebio/test/data/test_export.csv'
        self.query.export('csv', filename=test_file)
        self.assertTrue(path.isfile(test_file))
        self.assertEqual(
            hashlib.sha1(open(test_file, 'rb').read()).hexdigest(),
            hashlib.sha1(open(reference_file, 'rb').read()).hexdigest()
        )
        remove(test_file)

    # XLSXExporter
    def test_excel_exporter(self):
        test_file = '/tmp/test_export.xlsx'
        # reference_file = 'solvebio/test/data/test_export.xlsx'
        self.query.export('excel', filename=test_file)
        self.assertTrue(path.isfile(test_file))
        remove(test_file)

    # JSONExporter
    def test_json_exporter(self):
        test_file = '/tmp/test_export.json'
        reference_file = 'solvebio/test/data/test_export.json'
        self.query.export('json', filename=test_file)
        self.assertTrue(path.isfile(test_file))
        self.assertEqual(
            hashlib.sha1(open(test_file, 'rb').read()).hexdigest(),
            hashlib.sha1(open(reference_file, 'rb').read()).hexdigest()
        )
        with open(test_file, 'r') as f:
            for row in f:
                self.assertTrue(json.loads(row))
        remove(test_file)
