from __future__ import absolute_import
from solvebio.resource import Dataset

from .helper import SolveBioTestCase

from os import path, remove
import json


class ExportsTests(SolveBioTestCase):
    """
    Test exporting SolveBio Query object.
    """
    # CSVExporter
    def test_csv_exporter(self):
        dataset = Dataset.retrieve(self.TEST_DATASET_NAME)
        query = dataset.query()[:10]

        query.export('csv', filename='/tmp/test.csv')
        self.assertTrue(path.isfile('/tmp/test.csv'))
        remove('/tmp/test.csv')

    # FlatCSVExporter
    def test_flat_csv_exporter(self):
        dataset = Dataset.retrieve(self.TEST_DATASET_NAME)
        query = dataset.query()[:10]

        query.export('flat-csv', filename='/tmp/test_flat.csv')
        self.assertTrue(path.isfile('/tmp/test_flat.csv'))
        remove('/tmp/test_flat.csv')

    # JSONExporter
    def test_json_exporter(self):
        dataset = Dataset.retrieve(self.TEST_DATASET_NAME)
        query = dataset.query()[:10]

        query.export('json', filename='/tmp/test.json')
        self.assertTrue(path.isfile('/tmp/test.json'))
        with open('/tmp/test.json', 'r') as f:
            for row in f:
                self.assertTrue(json.loads(row))
        remove('/tmp/test.json')
