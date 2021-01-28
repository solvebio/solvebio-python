from solvebio import Filter
from solvebio.test.helper import SolveBioTestCase


class BaseFileQueryTest(SolveBioTestCase):
    """Test File Queries"""

    def setUp(self):
        super(BaseFileQueryTest, self).setUp()
        self.file = self.client.Object.get_by_full_path(
            self.TEST_FILE_FULL_PATH)

    def test_basic(self):
        results = self.file.query().filter(
            hgnc_id__in=['HGNC:5',
                         'HGNC:37133',
                         'HGNC:24086']
        )

        self.assertEqual(results.total, 3)
        self.assertEqual(len(results), results.total)

        # Test that iteration returns the correct number of results.
        # Test iterating through result-sets that are smaller than
        # the page size.
        self.assertEqual(len(results), len([r for r in results]))

    def test_basic_with_limit(self):
        limit = 10
        results = self.file.query(limit=limit)
        self.assertEqual(len(results), limit)

        # test that iteration returns the correct number of results.
        self.assertEqual(len([r for r in results]), limit)

    def test_count(self):
        q = self.file.query()
        total = q.count()
        self.assertGreater(total, 0)

        q = self.file.query().filter(hgnc_id='HGNC:5')
        self.assertEqual(q.count(), 1)

        # invalid filter
        q = self.file.query().filter(hgnc_id='foo')
        self.assertEqual(q.count(), 0)

    def test_count_with_limit(self):
        q = self.file.query()
        total = q.count()
        self.assertGreater(total, 0)

        for limit in [1, 10, 1000]:
            q = self.file.query(limit=limit).filter(hgnc_id='HGNC:5')
            self.assertEqual(q.count(), 1)

            # invalid filter
            q = self.file.query(limit=limit).filter(hgnc_id='foo')
            self.assertEqual(q.count(), 0)

    def test_len(self):
        q = self.file.query()
        total = q.count()
        self.assertGreater(total, 0)
        self.assertEqual(len(q), total)

        q = self.file.query().filter(hgnc_id='HGNC:5')
        self.assertEqual(len(q), 1)

        # invalid filter
        q = self.file.query().filter(hgnc_id='foo')
        self.assertEqual(len(q), 0)

    def test_len_with_limit(self):
        q = self.file.query()
        total = q.count()
        self.assertGreater(total, 0)
        self.assertEqual(len(q), total)

        for limit in [1, 10, 1000]:
            q = self.file.query(limit=limit).filter(hgnc_id='HGNC:5')
            self.assertEqual(len(q), 1 if limit > 0 else 0)

            # invalid filter
            q = self.file.query(limit=limit).filter(hgnc_id='foo')
            self.assertEqual(len(q), 0)

    def test_empty(self):
        # invalid filter
        results = self.file.query().filter(hgnc_id='foo')
        self.assertEqual(len(results), 0)
        self.assertEqual(results[:]._buffer, [])
        self.assertRaises(IndexError, lambda: results[0])

    def test_empty_with_limit(self):
        limit = 100

        # invalid filter
        results = self.file.query(limit=limit) \
            .filter(hgnc_id='foo')
        self.assertEqual(len(results), 0)
        self.assertEqual(results[:]._buffer, [])
        self.assertRaises(IndexError, lambda: results[0])

    def test_paging(self):
        page_size = 10
        num_pages = 3
        results = self.file.query(page_size=page_size)

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
        results = self.file.query(limit=limit, page_size=page_size)

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

        results = self.file.query(limit=limit)
        self.assertEqual(len(results[0:limit]), limit)

        results = self.file.query(limit=limit)
        self.assertEqual(len(results[:limit]), limit)

        results = self.file.query(limit=limit)
        self.assertEqual(len(results[limit:]), limit)

        r0 = self.file.query(limit=limit)[0:limit][limit - 1]
        r1 = self.file.query(limit=limit)[limit - 1:][0]
        self.assertEqual(r0['entrez_id'], r1['entrez_id'])

    def test_slice_ranges_with_paging(self):
        limit = 50
        page_size = 10

        results = self.file.query(limit=limit, page_size=page_size)
        self.assertEqual(len(results[0:limit]), limit)

        results = self.file.query(limit=limit, page_size=page_size)
        self.assertEqual(len(results[:limit]), limit)

        results = self.file.query(limit=limit, page_size=page_size)
        self.assertEqual(len(results[limit:]), limit)

        r0 = self.file.query(limit=limit)[0:limit][limit - 1]
        r1 = self.file.query(limit=limit)[limit - 1:][0]
        self.assertEqual(r0['entrez_id'], r1['entrez_id'])

    def test_slice_offsets(self):
        zero_two = self.file.query()[0:2]
        one_three = self.file.query()[1:3]

        # Ensure that the repr for [0:1] != [1:2]
        self.assertNotEqual(repr(zero_two), repr(one_three))

        # Ensure that the second repr for [0:2] == [1:3]
        self.assertEqual(repr(zero_two[1]), repr(one_three[0]))

    def test_slice_until_object_end(self):
        total = self.file.query(limit=1000).count()

        sliced_ds = self.file.query(limit=10)[total - 1:]

        left_records = 0
        for _ in sliced_ds:
            left_records += 1

        # Ensure that only one records has left in the file
        self.assertEqual(left_records, 1)

    def test_slice_ranges_with_small_limit(self):
        # Test slices larger than 'limit'

        limit = 1
        filters = Filter(**{'entrez_id__in': [str(i) for i in range(2, 13)]})
        results = self.file.query(limit=limit, filters=filters)[0:4]
        self.assertEqual(len(results), limit)

    def test_paging_and_slice_equivalence(self):
        idx0 = 3
        idx1 = 5
        filters = Filter(**{'entrez_id__in': [str(i) for i in range(2, 1000)]})

        def _query():
            return self.file.query(limit=10, filters=filters)

        results_slice = _query()[idx0:idx1]
        results_paging = []

        for (i, r) in enumerate(_query()):
            if i == idx1:
                break
            elif i >= idx0:
                results_paging.append(r)

        self.assertEqual(len(results_paging), len(results_slice))

    def test_field_filters(self):
        limit = 1
        results = self.file.query(limit=limit)
        self.assertEqual(len(results[0].keys()), 52)

        results = self.file.query(limit=limit, fields=['entrez_id'])
        self.assertEqual(len(results[0].keys()), 1)

        results = self.file.query(
            limit=limit, exclude_fields=['entrez_id'])
        self.assertEqual(len(results[0].keys()), 51)
        self.assertTrue('entrez_id' not in results[0].keys())
