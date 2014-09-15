"""Test Non Paging Queries"""
import unittest
import sys
import solvebio
sys.path.insert(0, '.')
from query_helper import SolveBioTestCase, TEST_DATASET_NAME
from solvebio import Dataset, Filter, BatchQuery, SolveError

# from mock import patch, Mock

class BaseQueryTest(SolveBioTestCase):
    def setUp(self):
        super(BaseQueryTest, self).setUp()
        self.dataset = Dataset.retrieve(TEST_DATASET_NAME)
        self.paging = False

    def test_limit(self):
        """
        When paging is off, len(results) should return the number of
        results retrieved.
        """
        limit = 10
        results = self.dataset.query(paging=self.paging, limit=limit)
        self.assertEqual(len(results), limit)

        for i in range(0, len(results)):
            # Python 2.6 compatability
            self.assertNotEqual(results[i], None)
        self.assertEqual(i, limit - 1)
        self.assertRaises(IndexError, lambda: results[limit])

    def test_limit_empty(self):
        """
        test Query when limit is specified and is GREATER THAN total available
        results.
        """
        limit = 100
        # bogus filter
        results = self.dataset.query(paging=self.paging, limit=limit) \
            .filter(hg19_start=1234)
        self.assertEqual(len(results), 0)

        for i in range(0, len(results)):
            self.fail()

        self.assertRaises(IndexError, lambda: results[0])

        results = self.dataset.query(paging=self.paging, limit=limit) \
            .filter(hg19_start=148459988)
        self.assertEqual(1, len(results))

    def test_limit_filter(self):
        """
        test Filtered Query in which limit is specified but is GREATER THAN
        the number of total available results
        """
        limit = 10
        num_filters = 3
        filters = Filter(hg19_start=148459988) | Filter(hg19_start=148562304) \
            | Filter(hg19_start=148891521)
        results = self.dataset.query(
            paging=self.paging, limit=limit, filters=filters)
        self.assertEqual(len(results), num_filters)

        for i in range(0, len(results)):
            # Python 2.6 compatability
            self.assertNotEqual(results[i], None)
        self.assertEqual(i, num_filters - 1)

        self.assertRaises(IndexError, lambda: results[num_filters])

    # API_LIMIT_MAX = 10000
    # def test_limit_max(self):
    #     q = self.dataset.query(limit=API_LIMIT_MAX * 10)
    #     self.assertRaises(SolveError, lambda: len(q))


if __name__ == "__main__":
    unittest.main()
