import os
import re
import unittest

import solvebio
from solvebio import Dataset, Filter, BatchQuery, SolveError

# from mock import patch, Mock

TEST_DATASET_NAME = 'omim/0.0.1-1/omim'
API_LIMIT_MAX = 10000


class SolveBioTestCase(unittest.TestCase):
    def setUp(self):
        super(SolveBioTestCase, self).setUp()
        solvebio.api_key = os.environ.get('SOLVEBIO_API_KEY', None)

    # Python < 2.7 compatibility
    def assertRaisesRegexp(self, exception, regexp, callable, *args, **kwargs):
        try:
            callable(*args, **kwargs)
        except exception, err:
            if regexp is None:
                return True

            if isinstance(regexp, basestring):
                regexp = re.compile(regexp)
            if not regexp.search(str(err)):
                raise self.failureException('\'%s\' does not match \'%s\'' %
                                            (regexp.pattern, str(err)))
        else:
            raise self.failureException(
                '%s was not raised' % (exception.__name__,))


class BaseQueryTest(SolveBioTestCase):
    def setUp(self):
        super(BaseQueryTest, self).setUp()
        self.dataset = Dataset.retrieve(TEST_DATASET_NAME)
        self.paging = False

    # test Filtered Query in which limit is specified but is GREATER THAN
    #  the number of total available results
    def test_limit_filter(self):
        limit = 10
        num_filters = 3
        filters = Filter(omim_id=144650) | Filter(omim_id=144600) \
            | Filter(omim_id=145300)
        results = self.dataset.query(
            paging=self.paging, limit=limit, filters=filters)
        self.assertEqual(len(results), num_filters)

        for i in range(0, len(results)):
            # Python 2.6 compatability
            self.assertNotEqual(results[i], None)
        self.assertEqual(i, num_filters - 1)

        self.assertRaises(IndexError, lambda: results[num_filters])

    # test Query when limit is specified and is GREATER THAN total available
    #  results
    def test_limit_empty(self):
        limit = 100
        # bogus filter
        results = self.dataset.query(paging=self.paging, limit=limit) \
            .filter(omim_id=None)
        self.assertEqual(len(results), 0)

        for i in range(0, len(results)):
            self.fail()

        self.assertRaises(IndexError, lambda: results[0])

    # def test_limit_max(self):
    #     q = self.dataset.query(limit=API_LIMIT_MAX * 10)
    #     self.assertRaises(SolveError, lambda: len(q))


class PagingQueryTest(BaseQueryTest):
    def setUp(self):
        super(PagingQueryTest, self).setUp()
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
        total = 823
        results = self.dataset.query(paging=True, limit=limit) \
            .filter(omim_id__in=range(100000, 120000))

        self.assertEqual(len(results), total)

        for (i, r) in enumerate(results):
            continue
        self.assertEqual(i, total - 1)

    def test_slice(self):
        limit = 100
        results = self.dataset.query(paging=True, limit=limit) \
            .filter(omim_id__in=range(100000, 120000))[200:410]
        self.assertEqual(len(results), 210)

        results = self.dataset.query(paging=True, limit=limit) \
            .filter(omim_id__in=range(100000, 110000))[0:5]
        self.assertEqual(len(results), 5)

    def test_paging_and_slice_equivalence(self):
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
            id_a = results_slice[i]['omim_id']
            id_b = results_cached[i]['omim_id']
            self.assertEqual(id_a, id_b)


class QueryTest(BaseQueryTest):
    def setUp(self):
        super(QueryTest, self).setUp()
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


class BatchQueryTest(SolveBioTestCase):
    def setUp(self):
        self.dataset = Dataset.retrieve(TEST_DATASET_NAME)
        super(BatchQueryTest, self).setUp()

    def test_invalid_batch_query(self):
        def test(self):
            BatchQuery([
                self.dataset.query(limit=1, fields=['bogus_field']),
                self.dataset.query(limit=10).filter(omim_id__gt=100000)
            ]).execute()

        self.assertRaises(SolveError, test, self)

    def test_batch_query(self):
        queries = [
            self.dataset.query(limit=1),
            self.dataset.query(limit=10).filter(omim_id__gt=100000)
        ]
        results = BatchQuery(queries).execute()
        self.assertEqual(len(results), 2)
        self.assertEqual(len(results[0]['results']), 1)
        self.assertEqual(len(results[1]['results']), 10)
