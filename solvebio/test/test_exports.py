from __future__ import absolute_import
import filecmp
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
        self.query = self.dataset.query(filter=filters,
                                        genome_build='GRCh37', limit=10)

    # CSVExporter
    def test_csv_exporter(self):
        self.query.export('csv', filename='/tmp/test.csv')
        self.assertTrue(path.isfile('/tmp/test.csv'))
        self.assertTrue(filecmp.cmp('/tmp/test.csv',
                                    '/solvebio/test/'
                                    'data/reference_export.csv'))
        remove('/tmp/test.csv')

    # XLSXExporter
    def test_excel_exporter(self):
        self.query.export('excel', filename='/tmp/test.xlsx')
        self.assertTrue(path.isfile('/tmp/test.xlsx'))
        self.assertTrue(filecmp.cmp('/tmp/test.xlsx',
                                    '/solvebio/test/'
                                    'data/reference_export.xlsx'))
        remove('/tmp/test.xlsx')

    # JSONExporter
    def test_json_exporter(self):
        self.query.export('json', filename='/tmp/test.json')
        self.assertTrue(path.isfile('/tmp/test.json'))
        self.assertTrue(filecmp.cmp('/tmp/test.json',
                                    '/solvebio/test/data/'
                                    'reference_export.json'))
        with open('/tmp/test.json', 'r') as f:
            for row in f:
                self.assertTrue(json.loads(row))
        remove('/tmp/test.json')
