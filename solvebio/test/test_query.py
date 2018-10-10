from __future__ import absolute_import

from solvebio.query import Filter

from .helper import SolveBioTestCase
from six.moves import map
from six.moves import range


class BaseQueryTest(SolveBioTestCase):
    """Test Paging Queries"""
    def setUp(self):
        super(BaseQueryTest, self).setUp()
        self.dataset = self.client.Dataset.get_by_full_path(
            self.TEST_DATASET_FULL_PATH)

    def test_basic(self):
        results = self.dataset.query().filter(
            omim_ids__in=[123631, 123670, 123690, 306250])
        self.assertEqual(results.total, 4)
        self.assertEqual(len(results), results.total)

        # Test that iteration returns the correct number of results.
        # Test iterating through result-sets that are smaller than
        # the page size.
        self.assertEqual(len(results), len([r for r in results]))

    def test_basic_with_limit(self):
        limit = 10
        results = self.dataset.query(limit=limit)
        self.assertEqual(len(results), limit)
        self.assertRaises(IndexError, lambda: results[results.total + 1])

        # test that iteration returns the correct number of results.
        self.assertEqual(len([r for r in results]), limit)

    def test_count(self):
        q = self.dataset.query()
        total = q.count()
        self.assertGreater(total, 0)

        # with a filter
        q = self.dataset.query().filter(omim_ids=123631)
        self.assertEqual(q.count(), 1)

        # with a bogus filter
        q = self.dataset.query().filter(omim_ids=999999)
        self.assertEqual(q.count(), 0)

    def test_count_with_limit(self):
        q = self.dataset.query()
        total = q.count()
        self.assertGreater(total, 0)

        for limit in [0, 10, 1000]:
            # with a filter
            q = self.dataset.query(limit=limit).filter(omim_ids=123631)
            self.assertEqual(q.count(), 1)

            # with a bogus filter
            q = self.dataset.query(limit=limit).filter(omim_ids=999999)
            self.assertEqual(q.count(), 0)

    def test_len(self):
        q = self.dataset.query()
        total = q.count()
        self.assertGreater(total, 0)
        self.assertEqual(len(q), total)

        # with a filter
        q = self.dataset.query().filter(omim_ids=123631)
        self.assertEqual(len(q), 1)

        # with a bogus filter
        q = self.dataset.query().filter(omim_ids=999999)
        self.assertEqual(len(q), 0)

    def test_len_with_limit(self):
        q = self.dataset.query()
        total = q.count()
        self.assertGreater(total, 0)
        self.assertEqual(len(q), total)

        for limit in [0, 10, 1000]:
            # with a filter
            q = self.dataset.query(limit=limit).filter(omim_ids=123631)
            self.assertEqual(len(q), 1 if limit > 0 else 0)

            # with a bogus filter
            q = self.dataset.query(limit=limit).filter(omim_ids=999999)
            self.assertEqual(len(q), 0)

    def test_empty(self):
        """
        test Query when limit is specified and is GREATER THAN total available
        results.
        """
        # bogus filter
        results = self.dataset.query().filter(omim_ids=999999)
        self.assertEqual(len(results), 0)
        self.assertEqual(results[:]._buffer, [])
        self.assertRaises(IndexError, lambda: results[0])

    def test_empty_with_limit(self):
        """
        test Query when limit is specified and is GREATER THAN total available
        results.
        """
        limit = 100
        # bogus filter
        results = self.dataset.query(limit=limit) \
            .filter(omim_ids=999999)
        self.assertEqual(len(results), 0)
        self.assertEqual(results[:]._buffer, [])
        self.assertRaises(IndexError, lambda: results[0])

    def test_filter(self):
        """
        test Filtered Query in which limit is specified but is GREATER THAN
        the number of total available results
        """
        num_filters = 4
        filters = \
            Filter(omim_ids=123631) | \
            Filter(omim_ids=123670) | \
            Filter(omim_ids=123690) | \
            Filter(omim_ids=306250)
        results = self.dataset.query(filters=filters)
        self.assertEqual(len(results), num_filters)
        self.assertRaises(IndexError, lambda: results[num_filters])

    def test_filter_with_limit(self):
        """
        test Filtered Query in which limit is specified but is GREATER THAN
        the number of total available results
        """
        limit = 10
        num_filters = 4
        filters = \
            Filter(omim_ids=123631) | \
            Filter(omim_ids=123670) | \
            Filter(omim_ids=123690) | \
            Filter(omim_ids=306250)
        results = self.dataset.query(
            limit=limit, filters=filters)
        self.assertEqual(len(results), num_filters)
        self.assertRaises(IndexError, lambda: results[num_filters])

    def test_paging(self):
        page_size = 10
        num_pages = 3
        results = self.dataset.query(page_size=page_size)

        _results = []
        for (i, r) in enumerate(results):
            # fetch three pages and break
            if i / page_size == num_pages:
                break
            _results.append(r)

        self.assertEqual(len(_results), num_pages * page_size)
        self.assertEqual(
            len(set(map(str, _results))),
            num_pages * page_size
        )

    def test_paging_with_limit(self):
        page_size = 10
        num_pages = 3
        limit = num_pages * page_size - 1
        results = self.dataset.query(limit=limit, page_size=page_size)

        _results = []
        for (i, r) in enumerate(results):
            _results.append(r)

        self.assertEqual(len(_results), limit)
        self.assertEqual(
            len(set(map(str, _results))),
            limit
        )

    def test_slice_ranges(self):
        limit = 50

        results = self.dataset.query(limit=limit)
        self.assertEqual(len(results[0:limit]), limit)

        results = self.dataset.query(limit=limit)
        self.assertEqual(len(results[:limit]), limit)

        results = self.dataset.query(limit=limit)
        self.assertEqual(len(results[limit:]), limit)

        r0 = self.dataset.query(limit=limit)[0:limit][limit - 1]
        r1 = self.dataset.query(limit=limit)[limit - 1:][0]
        self.assertEqual(r0['hgnc_id'], r1['hgnc_id'])

    def test_slice_ranges_with_paging(self):
        limit = 50
        page_size = 10

        results = self.dataset.query(limit=limit, page_size=page_size)
        self.assertEqual(len(results[0:limit]), limit)

        results = self.dataset.query(limit=limit, page_size=page_size)
        self.assertEqual(len(results[:limit]), limit)

        results = self.dataset.query(limit=limit, page_size=page_size)
        self.assertEqual(len(results[limit:]), limit)

        r0 = self.dataset.query(limit=limit)[0:limit][limit - 1]
        r1 = self.dataset.query(limit=limit)[limit - 1:][0]
        self.assertEqual(r0['hgnc_id'], r1['hgnc_id'])

    def test_slice_offsets(self):
        zero_two = self.dataset.query()[0:2]
        one_three = self.dataset.query()[1:3]

        # Ensure that the repr for [0:1] != [1:2]
        self.assertNotEqual(repr(zero_two), repr(one_three))

        # Ensure that the second repr for [0:2] == [1:3]
        self.assertEqual(repr(zero_two[1]), repr(one_three[0]))

    def test_slice_ranges_with_small_limit(self):
        # Test slices larger than 'limit'
        limit = 1
        results = self.dataset.query(limit=limit) \
            .filter(hgnc_id__range=(1000, 2000))[0:4]
        self.assertEqual(len(results), limit)

    def test_paging_and_slice_equivalence(self):
        idx0 = 3
        idx1 = 5

        def _query():
            return self.dataset.query(limit=10) \
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

        q = self.dataset.query(limit=100)
        results_slice = q[idx0:idx1]
        results_cached = q[idx0:idx1]
        self.assertEqual(len(results_slice), len(results_cached))
        for i in range(0, len(results_slice)):
            id_a = results_slice[i]['chromosome']
            id_b = results_cached[i]['chromosome']
            self.assertEqual(id_a, id_b)

    def test_get_by_index(self):
        limit = 100
        page_size = 10
        idxs = [0, 1, 10, 20, 50, 99]
        q = self.dataset.query(limit=limit, page_size=page_size)
        cached = []
        for idx in idxs:
            cached.append(q[idx])

        # forwards
        for (i, idx) in enumerate(idxs):
            self.assertEqual(cached[i], q[idx])

        # backwards
        for (i, idx) in reversed(list(enumerate(idxs))):
            self.assertEqual(cached[i], q[idx])

    def test_field_filters(self):
        limit = 1
        results = self.dataset.query(limit=limit)
        self.assertEqual(len(results[0].keys()), 41)

        results = self.dataset.query(limit=limit, fields=['hgnc_id'])
        self.assertEqual(len(results[0].keys()), 1)

        results = self.dataset.query(
            limit=limit, exclude_fields=['hgnc_id'])
        self.assertEqual(len(results[0].keys()), 40)
        self.assertTrue('hgnc_id' not in results[0].keys())

    def test_entity_filters(self):
        entities = [('gene', 'BRCA2')]
        query = self.dataset.query(entities=entities)
        self.assertEqual(query.count(), 1)
