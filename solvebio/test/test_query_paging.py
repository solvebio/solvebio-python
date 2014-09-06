"""Test Paging Queries"""
import unittest
import sys
import solvebio
sys.path.insert(0, '.')
from query_helper import SolveBioTestCase, TEST_DATASET_NAME
from solvebio import Dataset, Filter, BatchQuery, SolveError

class PagingQueryTest(SolveBioTestCase):
    def setUp(self):
        super(PagingQueryTest, self).setUp()
        self.dataset = Dataset.retrieve(TEST_DATASET_NAME)
        self.paging = True

    def no_test_limit(self):
        """
        In paging queries, len(results) should return the total # of results
        that exist.
        """
        limit = 10
        results = self.dataset.query(paging=True, limit=limit)
        self.assertEqual(len(results), results.total)

    def test_paging(self):
        limit = 100
        total = 2012
        results = self.dataset.query(paging=True, limit=limit) \
            .filter(hg19_start__range = (140000000, 150000000))

        self.assertEqual(len(results), total)

        for (i, r) in enumerate(results):
            continue
        self.assertEqual(i, total - 1)

    def no_test_slice(self):
        limit = 100
        results = self.dataset.query(paging=True, limit=limit) \
            .filter(hg19_start__range = (140000000, 150000000))[200:410]
        self.assertEqual(len(results), 210)

        results = self.dataset.query(paging=True, limit=limit) \
            .filter(omim_id__in=range(100000, 110000))[0:5]
        self.assertEqual(len(results), 5)

    def no_test_paging_and_slice_equivalence(self):
        idx0 = 60
        idx1 = 81

        def _query():
            return self.dataset.query(paging=True, limit=10) \
                .filter(omim_id__in=range(100000, 120000))

        results_slice = _query()[idx0:idx1]
        results_paging = []
        for (i, r) in enumerate(_query()):
            if i == idx1:
                break
            elif i >= idx0:
                results_paging.append(r)

        self.assertEqual(len(results_paging), len(results_slice))

        for i in range(0, len(results_slice)):
            id_a = results_paging[i]['omim_id']
            id_b = results_slice[i]['omim_id']
            self.assertEqual(id_a, id_b)

    def no_test_caching(self):
        idx0 = 60
        idx1 = 81

        q = self.dataset.query(paging=True, limit=100)
        # q = self.dataset.query(paging=True, limit=100) \
        #         .filter(omim_id__in=range(100000, 120000))
        results_slice = q[idx0:idx1]
        results_cached = q[idx0:idx1]

        self.assertEqual(len(results_slice), len(results_cached))
        for i in range(0, len(results_slice)):
            id_a = results_slice[i]['omim_id']
            id_b = results_cached[i]['omim_id']
            self.assertEqual(id_a, id_b)


if __name__ == "__main__":
    unittest.main()
