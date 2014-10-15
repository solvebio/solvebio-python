"""Test Paging Queries"""
import unittest
import sys
import os
sys.path.insert(0, '.')
from query_helper import SolveBioTestCase, TEST_DATASET_NAME
from solvebio import Dataset


@unittest.skipIf('SOLVEBIO_API_HOST' in os.environ and \
                 os.environ['SOLVEBIO_API_HOST'] == 'http://127.0.0.1:8000',
                 "showing class skipping")
class PagingQueryTest(SolveBioTestCase):
    def setUp(self):
        super(PagingQueryTest, self).setUp()
        self.dataset = Dataset.retrieve(TEST_DATASET_NAME)
        self.paging = True

    def test_limit(self):
        """
        In paging queries, len(results) should return the total # of results
        that exist.
        """
        limit = 10
        results = self.dataset.query(paging=True, limit=limit)
        self.assertEqual(len(results), results.total)

    def test_paging(self):
        limit = 100
        total = 7
        results = self.dataset.query(paging=True, limit=limit) \
          .filter(hg19_start__range=(140000000, 140050000))

        self.assertEqual(len(results), total)

        for (i, r) in enumerate(results):
            continue
        self.assertEqual(i, total - 1)

    def test_slice(self):
        limit = 100
        results = self.dataset.query(paging=True, limit=limit) \
            .filter(hg19_start__range=(140000000, 140050000))[2:5]
        self.assertEqual(len(results), 3)

        results = self.dataset.query(paging=True, limit=limit) \
            .filter(hg19_start__in=range(140000000, 140050000))[0:8]
        self.assertEqual(len(results), 7)

    def test_paging_and_slice_equivalence(self):
        idx0 = 3
        idx1 = 5

        def _query():
            return self.dataset.query(paging=True, limit=20) \
                .filter(hg19_start__range=(140000000, 140060000))[2:10]

        results_slice = _query()[idx0:idx1]
        results_paging = []
        for (i, r) in enumerate(_query()):
            if i == idx1:
                break
            elif i >= idx0:
                results_paging.append(r)

        self.assertEqual(len(results_paging), len(results_slice))

        for i in range(0, len(results_slice)):
            id_a = results_paging[i]['hg19_start']
            id_b = results_slice[i]['hg19_start']
            self.assertEqual(id_a, id_b)

    def test_caching(self):
        idx0 = 60
        idx1 = 81

        q = self.dataset.query(paging=True, limit=100)
        # q = self.dataset.query(paging=True, limit=100) \
        #         .filter(omim_id__in=range(100000, 120000))
        results_slice = q[idx0:idx1]
        results_cached = q[idx0:idx1]

        self.assertEqual(len(results_slice), len(results_cached))
        for i in range(0, len(results_slice)):
            id_a = results_slice[i]['reference_allele']
            id_b = results_cached[i]['reference_allele']
            self.assertEqual(id_a, id_b)


if __name__ == "__main__":
    unittest.main()
