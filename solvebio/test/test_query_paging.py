from solvebio.resource import Dataset

from .helper import unittest, SolveBioTestCase


class PagingQueryTest(SolveBioTestCase):
    """Test Paging Queries"""
    def setUp(self):
        super(PagingQueryTest, self).setUp()
        self.dataset = Dataset.retrieve(self.TEST_DATASET_NAME)
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
        limit = 1
        # There should be 4 results with this filter
        total = 4
        results = self.dataset.query(paging=True, limit=limit) \
            .filter(hgnc_id__in=[2396, 2404, 2409, 2411])

        # In paging queries, len(results) should return the total number
        # of results available on the server.
        self.assertEqual(len(results), results.total)

        for (i, r) in enumerate(results):
            continue

        self.assertEqual(i, total - 1)

    def test_slice(self):
        # Test slices larger than 'limit'
        results = self.dataset.query(paging=True, limit=1) \
            .filter(hgnc_id__range=(1000, 2000))[1:4]
        self.assertEqual(len(results), 3)

    def test_paging_and_slice_equivalence(self):
        idx0 = 3
        idx1 = 5

        def _query():
            return self.dataset.query(paging=True, limit=10) \
                .filter(hgnc_id__range=(1000, 5000))

        results_slice = _query()[idx0:idx1]
        results_paging = []

        for (i, r) in enumerate(_query()):
            if i == idx1:
                break
            elif i >= idx0:
                results_paging.append(r)

        self.assertEqual(len(results_paging), len(results_slice))

        for i in range(0, len(results_slice)):
            id_a = results_paging[i]['hgnc_id']
            id_b = results_slice[i]['hgnc_id']
            self.assertEqual(id_a, id_b)

    def test_caching(self):
        idx0 = 60
        idx1 = 81

        q = self.dataset.query(paging=True, limit=100)
        results_slice = q[idx0:idx1]
        results_cached = q[idx0:idx1]

        self.assertEqual(len(results_slice), len(results_cached))
        for i in range(0, len(results_slice)):
            id_a = results_slice[i]['chromosome']
            id_b = results_cached[i]['chromosome']
            self.assertEqual(id_a, id_b)


if __name__ == "__main__":
    unittest.main()
