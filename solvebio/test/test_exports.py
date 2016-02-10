from __future__ import absolute_import
from solvebio.resource import Dataset

from .helper import SolveBioTestCase
# import unittest
from os import path, remove

try:
    import pandas
except ImportError:
    pandas = None


class ExportsTests(SolveBioTestCase):
    """
    Test exporting SolveBio Query object
    to pandas DataFrame and CSV.
    """

    # @unittest.skipIf(skip, 'pandas library must be installed')
    # def test_pandas_exporter(self):
    #     dataset = Dataset.retrieve(self.TEST_DATASET_NAME)
    #     query = dataset.query()[:10]
    #
    #     df = query.export('pandas')
    #     self.assertTrue(isinstance(df, pd.DataFrame))

    def test_csv_exportes(self):
        dataset = Dataset.retrieve(self.TEST_DATASET_NAME)
        query = dataset.query()[:10]

        query.export('csv', filename='/tmp/test.csv')
        self.assertTrue(path.isfile('/tmp/test.csv'))
        remove('/tmp/test.csv')
