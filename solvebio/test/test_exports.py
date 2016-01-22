from __future__ import absolute_import
from solvebio.resource import Dataset

from .helper import SolveBioTestCase
import unittest
from os import path, remove

try:
    import pandas as pd
    skip = False
except ImportError:
    skip = True


class ExportsTests(SolveBioTestCase):
    """
    Test exporting SolveBio Query object
    to pandas DataFrame and CSV.
    """

    @unittest.skipIf(skip, 'pandas library must be installed')
    def test_data_frame(self):
        dataset = Dataset.retrieve(self.TEST_DATASET_NAME)
        query = dataset.query()[:10]

        df = query.to_data_frame()
        self.assertTrue(isinstance(df, pd.DataFrame))

    @unittest.skipIf(skip, 'pandas library must be installed')
    def test_csv(self):
        dataset = Dataset.retrieve(self.TEST_DATASET_NAME)
        query = dataset.query()[:20]

        query.to_csv('query.csv')

        self.assertTrue(path.isfile('query.csv'))
        remove('query.csv')
