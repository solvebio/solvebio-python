import os
import re
import unittest

import solvebio
from solvebio import *

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


class QueryTest(SolveBioTestCase):
    def setUp(self):
        super(QueryTest, self).setUp()
        self.dataset = Dataset.retrieve(TEST_DATASET_NAME)


# TODO
class BaseQueryTest(QueryTest):
    pass


class QueryLimitTest(QueryTest):
    # test Query when limit is specified and is LESS THAN the number of
    # total available results
    def test_limit(self):
        limit = 10
        results = self.dataset.query(limit=limit)
        self.assertEqual(len(results), limit)

        for i in range(0, len(results)):
            # Python 2.6 compatability
            self.assertNotEqual(results[i], None)
        self.assertEqual(i, limit - 1)

        self.assertRaises(Exception, lambda: results[limit])

    # test Filtered Query in which limit is specified but is GREATER THAN
    #  the number of total available results
    def test_limit_filter(self):
        limit = 10
        num_filters = 3
        filters = Filter(omim_id=144650) | Filter(omim_id=144600) \
            | Filter(omim_id=145300)
        results = self.dataset.query(limit=limit, filters=filters)
        self.assertEqual(len(results), num_filters)

        for i in range(0, len(results)):
            # Python 2.6 compatability
            self.assertNotEqual(results[i], None)
        self.assertEqual(i, num_filters - 1)

        self.assertRaises(Exception, lambda: results[num_filters])

    # test Query when limit is specified and is GREATER THAN total available
    #  results
    def test_limit_empty(self):
        limit = 10
        # bogus filter
        results = self.dataset.query(limit=limit).filter(omim_id=None)
        self.assertEqual(len(results), 0)

        for i in range(0, len(results)):
            self.fail()

        self.assertRaises(Exception, lambda: results[0])

    def test_limit_max(self):
        q = self.dataset.query(limit=API_LIMIT_MAX * 10)
        self.assertRaises(SolveError, lambda: len(q))


# class QueryNoLimitTest(QueryTest):
#     # test Query without a limit param and ensure that max returned results
#     #  is 10000
#     def test_no_limit(self):
#         results = self.dataset.query()
#         self.assertEqual(len(results), API_LIMIT_MAX)
