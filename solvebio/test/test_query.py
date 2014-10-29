from solvebio.resource import Dataset
from solvebio.query import Filter

from helper import SolveBioTestCase


class BaseQueryTest(SolveBioTestCase):
    """Test Non-Paging Queries"""
    def setUp(self):
        super(BaseQueryTest, self).setUp()
        self.dataset = Dataset.retrieve(self.TEST_DATASET_NAME)
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
            .filter(omim_ids=999999)
        self.assertEqual(len(results), 0)

        for i in range(0, len(results)):
            self.fail()

        self.assertRaises(IndexError, lambda: results[0])

        results = self.dataset.query(paging=self.paging, limit=limit) \
            .filter(omim_ids=123631)
        self.assertEqual(1, len(results))

    def test_limit_filter(self):
        """
        test Filtered Query in which limit is specified but is GREATER THAN
        the number of total available results
        """
        limit = 10
        num_filters = 2
        filters = Filter(omim_ids=123631) | Filter(omim_ids=123670)
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
        self.assertEqual(r0['hgnc_id'], r1['hgnc_id'])
