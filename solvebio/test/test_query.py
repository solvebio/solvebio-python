import os
import re
import unittest
import solvebio

# from mock import patch, Mock


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
                raise self.failureException('"%s" does not match "%s"' %
                                            (regexp.pattern, str(err)))
        else:
            raise self.failureException(
                '%s was not raised' % (exception.__name__,))


class QueryTests(SolveBioTestCase):
    # TODO
    def test_dummy(self):
        # self.assertRaises(AttributeError, getattr, obj, 'myattr')
        # self.assertRaises(KeyError, obj.__getitem__, 'myattr')
        self.assertEqual(True, True)
