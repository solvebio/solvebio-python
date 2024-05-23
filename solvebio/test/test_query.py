from __future__ import absolute_import

import unittest

from solvebio.query import Filter
from solvebio import SolveError

from .helper import SolveBioTestCase
from six.moves import map
from six.moves import range


class BaseQueryTest(SolveBioTestCase):
    """Test Paging Queries"""
    def setUp(self):
        super(BaseQueryTest, self).setUp()
        self.dataset = self.client.Object.get_by_full_path(
            self.TEST_DATASET_FULL_PATH)
        self.dataset2 = self.client.Object.get_by_full_path(
            self.TEST_DATASET_FULL_PATH_2)

    def test_basic(self):
        results = self.dataset.query().filter(
            omim_id__in=['OMIM:123631',
                         'OMIM:123670',
                         'OMIM:123690',
                         'OMIM:306250'])
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
        q = self.dataset.query().filter(omim_id='OMIM:123631')
        self.assertEqual(q.count(), 1)

        # with a bogus filter
        q = self.dataset.query().filter(omim_id='OMIM:99999')
        self.assertEqual(q.count(), 0)

    def test_count_with_limit(self):
        q = self.dataset.query()
        total = q.count()
        self.assertGreater(total, 0)

        for limit in [0, 10, 1000]:
            # with a filter
            q = self.dataset.query(limit=limit).filter(omim_id='OMIM:123631')
            self.assertEqual(q.count(), 1)

            # with a bogus filter
            q = self.dataset.query(limit=limit).filter(omim_id='OMIM:99999')
            self.assertEqual(q.count(), 0)

    def test_len(self):
        q = self.dataset.query()
        total = q.count()
        self.assertGreater(total, 0)
        self.assertEqual(len(q), total)

        # with a filter
        q = self.dataset.query().filter(omim_id='OMIM:123631')
        self.assertEqual(len(q), 1)

        # with a bogus filter
        q = self.dataset.query().filter(omim_id='OMIM:999999')
        self.assertEqual(len(q), 0)

    def test_len_with_limit(self):
        q = self.dataset.query()
        total = q.count()
        self.assertGreater(total, 0)
        self.assertEqual(len(q), total)

        for limit in [0, 10, 1000]:
            # with a filter
            q = self.dataset.query(limit=limit).filter(omim_id='OMIM:123631')
            self.assertEqual(len(q), 1 if limit > 0 else 0)

            # with a bogus filter
            q = self.dataset.query(limit=limit).filter(omim_id='OMIM:999999')
            self.assertEqual(len(q), 0)

    def test_empty(self):
        """
        test Query when limit is specified and is GREATER THAN total available
        results.
        """
        # bogus filter
        results = self.dataset.query().filter(omim_id='OMIM:99999')
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
            .filter(omim_id='OMIM:99999')
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
            Filter(omim_id='OMIM:123631') | \
            Filter(omim_id='OMIM:123670') | \
            Filter(omim_id='OMIM:123690') | \
            Filter(omim_id='OMIM:306250')
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
            Filter(omim_id='OMIM:123631') | \
            Filter(omim_id='OMIM:123670') | \
            Filter(omim_id='OMIM:123690') | \
            Filter(omim_id='OMIM:306250')
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
        self.assertEqual(r0['entrez_id'], r1['entrez_id'])

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
        self.assertEqual(r0['entrez_id'], r1['entrez_id'])

    def test_slice_offsets(self):
        zero_two = self.dataset.query()[0:2]
        one_three = self.dataset.query()[1:3]

        # Ensure that the repr for [0:1] != [1:2]
        self.assertNotEqual(repr(zero_two), repr(one_three))

        # Ensure that the second repr for [0:2] == [1:3]
        self.assertEqual(repr(zero_two[1]), repr(one_three[0]))

    def test_slice_until_object_end(self):
        total = self.dataset.query(limit=0).count()

        sliced_ds = self.dataset.query(limit=10)[total - 1:]

        left_records = 0
        for _ in sliced_ds:
            left_records += 1

        # Ensure that only one records has left in the dataset
        self.assertEqual(left_records, 1)

    def test_slice_ranges_with_small_limit(self):
        # Test slices larger than 'limit'
        # query returns 6
        limit = 1
        results = self.dataset.query(limit=limit) \
            .filter(mamit_trnadb__range=(2, 12))[0:4]
        self.assertEqual(len(results), limit)

    def test_paging_and_slice_equivalence(self):
        idx0 = 3
        idx1 = 5

        def _query():
            return self.dataset.query(limit=10) \
                .filter(mamit_trnadb__range=(2, 12))

        results_slice = _query()[idx0:idx1]
        results_paging = []

        for (i, r) in enumerate(_query()):
            if i == idx1:
                break
            elif i >= idx0:
                results_paging.append(r)

        self.assertEqual(len(results_paging), len(results_slice))

        for i in range(0, len(results_slice)):
            id_a = results_paging[i]['entrez_id']
            id_b = results_slice[i]['entrez_id']
            self.assertEqual(id_a, id_b)

    def test_caching(self):
        idx0 = 60
        idx1 = 81

        q = self.dataset.query(limit=100)
        results_slice = q[idx0:idx1]
        results_cached = q[idx0:idx1]
        self.assertEqual(len(results_slice), len(results_cached))
        for i in range(0, len(results_slice)):
            id_a = results_slice[i]['status']
            id_b = results_cached[i]['status']
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
        self.assertEqual(len(results[0].keys()), 55)

        results = self.dataset.query(limit=limit, fields=['entrez_id'])
        self.assertEqual(len(results[0].keys()), 1)

        results = self.dataset.query(
            limit=limit, exclude_fields=['entrez_id'])
        self.assertEqual(len(results[0].keys()), 54)
        self.assertTrue('entrez_id' not in results[0].keys())

    def test_entity_filters(self):
        entities = [('gene', 'BRCA2')]
        query = self.dataset.query(entities=entities)
        self.assertEqual(query.count(), 1)

    def test_target_fields(self):

        # Invalid fields
        try:
            query = self.dataset.query(target_fields=[1])
        except SolveError as e:
            assert "{u'target_fields': [u'Invalid data']}" in e
            pass

        entities = [('gene', 'BRCA2')]
        query = self.dataset.query(
            entities=entities,
            target_fields=[dict(name='user', expression='user()["email"]')],
            limit=1)
        self.assertEqual(query.count(), 1)
        for record in query:
            assert "@solvebio.com" in record['user']

    def test_join(self):
        query_a = self.dataset2.query(fields=['gene'], limit=1).filter(gene='MAN2B1')
        query_b = self.dataset2.query(fields=['gene', 'variant'])
        join_query = query_a.join(query_b, key='gene')

        count = 0
        for row in join_query:
            self.assertTrue('b_gene' not in row)
            self.assertEqual(row['gene'], 'MAN2B1')
            count += 1
            if count == 10:
                break

    def test_join_custom_prefix(self):
        query_a = self.dataset2.query(fields=['gene', 'variant'], limit=1).filter(gene='MAN2B1')
        query_b = self.dataset2.query(fields=['gene', 'variant'])
        join_query = query_a.join(query_b, key='gene', prefix='query_b_')

        count = 0
        for row in join_query:
            self.assertTrue('query_b_variant' in row)
            count += 1
            if count == 10:
                break

    def test_join_enable_always_prefix(self):
        query_a = self.dataset2.query(fields=['gene'], limit=1).filter(gene='MAN2B1')
        query_b = self.dataset2.query(fields=['gene', 'variant'])
        join_query = query_a.join(query_b, key='gene', always_prefix=True)

        count = 0
        for row in join_query:
            self.assertTrue('b_variant' in row)
            count += 1
            if count == 10:
                break

    def test_join_empty_query_a(self):
        # Empty query_a
        query_a = self.dataset2.query(fields=['gene']).filter(gene='PoshRoyalGene')
        query_b = self.dataset2.query(fields=['gene'])
        join_query = query_a.join(query_b, key='gene')

        self.assertEqual(list(join_query), [])

    def test_join_empty_query_b(self):
        query_a = self.dataset2.query(fields=['gene'], limit=5).filter(gene='MAN2B1')
        # Empty query_b
        query_b = self.dataset2.query(fields=['gene']).filter(gene='PoshRoyalGene')
        join_query = query_a.join(query_b, key='gene')

        self.assertEqual(len(join_query), 5)

        for row in join_query:
            for key, value in row.items():
                if 'b_' in key:
                    self.assertEqual(value, None)

    def test_join_multiple_join(self):
        query_a = self.dataset2.query(fields=['gene'], limit=1).filter(gene='MAN2B1')
        query_b = self.dataset2.query(fields=['gene'])
        query_c = self.dataset2.query(fields=['gene'])

        join_query = query_a.join(query_b, key='gene', prefix='b_')
        multiple_join_query = join_query.join(query_c, key='gene', prefix='c_')

        for record in multiple_join_query:
            self.assertTrue('gene' in record)
            self.assertTrue('b_gene' in record)
            self.assertTrue('c_gene' in record)

    def test_join_with_list_key(self):
        """Test a join where the key is a list. In this case, clinical_significance is a list.
        Ensure that the output contains a single value in each resulting record."""

        annotator_params = {"pre_annotation_expression": "explode(record, ['clinical_significance'])"}
        query_a = self.dataset2\
            .query(
                fields=['clinical_significance', 'variant'],
                annotator_params=annotator_params)\
            .filter(gene='MAN2B1')\
            .limit(10)
        query_b = self.dataset2\
            .query(fields=['clinical_significance', 'gene'])\
            .filter(gene='MAN2B1')\
            .limit(10)

        for i in query_a.join(query_b, "clinical_significance"):
            self.assertFalse(isinstance(i['clinical_significance'], list))
            self.assertTrue('_errors' not in i)

    def test_join_with_list_values(self):
        """Test a join where one of the fields is a list.
        In this case, clinical_significance is a list.
        Ensure that the output contains a list of strings (not lists)."""

        annotator_params = {"pre_annotation_expression": "explode(record, ['clinical_significance'])"}
        query_a = self.dataset2\
            .query(
                fields=['clinical_significance', 'variant'],
                annotator_params=annotator_params)\
            .filter(gene='MAN2B1')\
            .limit(10)
        query_b = self.dataset2\
            .query(fields=['clinical_significance', 'gene', 'variant'])\
            .filter(gene='MAN2B1')\
            .limit(10)

        for i in query_a.join(query_b, "variant"):
            # Since each value contains one element, the resulting output is just a flat string
            # as the API takes the first value in the list.
            self.assertFalse(isinstance(i['clinical_significance'], list))
            self.assertFalse(isinstance(i['b_clinical_significance'], list))
            self.assertTrue('_errors' not in i)

    def test_join_pagination(self):
        # 50 records total
        query_a = self.dataset2.query(fields=['gene'], limit=50, page_size=10).filter(gene='MAN2B1')
        # 367 records total which have gene='MAN2B1'
        query_b = self.dataset2.query(fields=['gene'])

        join_query = query_a.join(query_b, key='gene', prefix='b_')

        self.assertEqual(len(query_a), 50)
        self.assertEqual(len(query_b.filter(gene='MAN2B1')), 367)
        self.assertEqual(len(list(join_query)), 50 * 367)

    def test_join_query_with_key_b(self):
        query_a = self.dataset.query(
            fields=['agr', 'gene_symbol'],
            limit=50, page_size=10
        )
        query_b = self.dataset2.query(
            fields=['gene', 'variant']
        )
        join_query = query_a.join(
            query_b, key='gene', key_b='variant', always_prefix=True
        )
        for record in join_query:
            self.assertTrue('agr' in record)
            self.assertTrue('gene_symbol' in record)
            self.assertTrue('b_gene' in record)
            self.assertTrue('b_variant' in record)

    @unittest.skip("Skip because API Host on GH pipelines doesn't host file at TEST_LARGE_TSV_FULL_PATH")
    def test_query_large_file_into_dataframe(self):
        import pandas as pd
        expected_num_rows = 1015

        try:
            large_object = self.client.Object.get_by_full_path(self.TEST_LARGE_TSV_FULL_PATH)
            query = large_object.query()
            dataframe = pd.DataFrame(query)
        except Exception as e:
            self.fail("Exception {} was raised while querying large object".format(e))
        self.assertTrue(not dataframe.empty)
        self.assertEqual(expected_num_rows, len(dataframe))
