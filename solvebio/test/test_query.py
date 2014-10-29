"""Test Non-Paging Queries"""
from test_helper import unittest
import os

from query_helper import SolveBioTestCase, TEST_DATASET_NAME
from solvebio.resource import Dataset
from solvebio.query import Filter


@unittest.skipIf('SOLVEBIO_API_HOST' in os.environ and
                 os.environ['SOLVEBIO_API_HOST'] == 'http://127.0.0.1:8000',
                 "showing class skipping")
class BaseQueryTest(SolveBioTestCase):
    def setUp(self):
        super(BaseQueryTest, self).setUp()
        self.dataset = Dataset.retrieve(TEST_DATASET_NAME)
        self.paging = False

    def test_limit(self):
        """
        When paging is off, len(total) should return the number of
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
        test Query when limit is specified and is GREATER THAN total
        available results.
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

    def test_slice_ranges(self):
        limit = 50

        query = self.dataset.query(paging=self.paging, limit=limit)
        self.assertEqual(len(query), limit)

        query = self.dataset.query(paging=self.paging, limit=limit)
        self.assertEqual(len(query[0:limit]), limit)

        query = self.dataset.query(paging=self.paging, limit=limit)
        self.assertEqual(len(query[:limit]), limit)

        query = self.dataset.query(paging=self.paging, limit=limit)
        self.assertEqual(len(query[limit:]), limit)

        # equality test
        r0 = self.dataset.query(paging=self.paging, limit=limit)[0:limit][-1]
        r1 = self.dataset.query(paging=self.paging, limit=limit)[limit - 1:][0]
        self.assertEqual(r0['rcvaccession'], r1['rcvaccession'])


if __name__ == "__main__":
    unittest.main()
