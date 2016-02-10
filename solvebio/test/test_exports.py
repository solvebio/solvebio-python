from __future__ import absolute_import
from solvebio.resource import Dataset

from .helper import SolveBioTestCase
# import unittest
from os import path, remove


class ExportsTests(SolveBioTestCase):
    """
    Test exporting SolveBio Query object.
    """

    def test_csv_exporter(self):
        dataset = Dataset.retrieve(self.TEST_DATASET_NAME)
        query = dataset.query()[:10]

        query.export('csv', filename='/tmp/test.csv')
        self.assertTrue(path.isfile('/tmp/test.csv'))
        remove('/tmp/test.csv')
