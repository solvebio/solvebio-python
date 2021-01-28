from __future__ import absolute_import
import six

import os
import re
import sys

if (sys.version_info >= (2, 7, 0)):
    import unittest   # NOQA
else:
    import unittest2 as unittest  # NOQA

import solvebio


class SolveBioTestCase(unittest.TestCase):
    TEST_DATASET_FULL_PATH = 'solvebio:public:/HGNC/3.3.0-2020-10-29/HGNC'
    TEST_DATASET_FULL_PATH_2 = 'solvebio:public:/ClinVar/5.1.0-20200720/Variants-GRCH38'
    TEST_FILE_FULL_PATH = 'solvebio:public:/HGNC/3.3.0-2020-10-29/hgnc_1000_rows.txt'

    def setUp(self):
        super(SolveBioTestCase, self).setUp()
        api_key = os.environ.get('SOLVEBIO_API_KEY', None)
        api_host = os.environ.get('SOLVEBIO_API_HOST', None)
        self.client = solvebio.SolveClient(host=api_host, token=api_key)

    def check_response(self, response, expect, msg):
        subset = [(key, response[key]) for
                  key in [x[0] for x in expect]]
        self.assertEqual(subset, expect)

    # Python < 2.7 compatibility
    def assertRaisesRegexp(self, exception, regexp, callable, *args, **kwargs):
        try:
            callable(*args, **kwargs)
        except exception as err:
            if regexp is None:
                return True

            if isinstance(regexp, six.string_types):
                regexp = re.compile(regexp)
            if not regexp.search(str(err)):
                raise self.failureException('\'%s\' does not match \'%s\'' %
                                            (regexp.pattern, str(err)))
        else:
            raise self.failureException(
                '%s was not raised' % (exception.__name__,))
