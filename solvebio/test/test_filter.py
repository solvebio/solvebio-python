import unittest

import solvebio
from solvebio import Filter


class FilterTest(unittest.TestCase):

    def test_filter_basic(self):
        f = solvebio.Filter()
        self.assertEqual(repr(f), '<Filter []>', 'empty filter')
        self.assertEqual(repr(~f), '<Filter []>', '"not" of empty filter')

        # Because the order in listing keys is arbitrary, we only
        # test with one entry.
        f1 = solvebio.Filter(price='Free')
        self.assertEqual(repr(f1), "<Filter [('price', 'Free')]>")
        self.assertEqual(repr(~~f1), "<Filter [('price', 'Free')]>",
                         '"not" of empty filter')

        a = solvebio.query.Filter(chr1="3")
        b = solvebio.query.Filter(chr2="4")
        self.assertEqual(repr(a | b),
                         "<Filter [{'or': [('chr1', '3'), ('chr2', '4')]}]>",
                         '"or" filter')

        f |= a
        self.assertEqual(repr(f), "<Filter [('chr1', '3')]>",
                         "'or' with empty filter")
        self.assertEqual(repr(a), "<Filter [('chr1', '3')]>",
                         "prior 'or' doesn't mung filter")

        filters3 = Filter(omim_id=144650) | Filter(omim_id=144600) \
          | Filter(omim_id=145300)
        self.assertEqual(repr(filters3),
                         "<Filter [{'or': [('omim_id', 144650)," +
                         " ('omim_id', 144600), ('omim_id', 145300)]}]>")

    def test_process_filters(self):
        # FIXME: add more and put in a loop.
        filters = [('omid', None)]
        expect = filters
        dataset_name = 'omim/0.0.1-1/omim'
        x = solvebio.PagingQuery(dataset_name)
        self.assertEqual(repr(x._process_filters(filters)), repr(expect))


if __name__ == "__main__":
    unittest.main()
