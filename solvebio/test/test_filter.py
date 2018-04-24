from __future__ import absolute_import
from __future__ import print_function

import unittest

import solvebio
from solvebio import Query, Filter, GenomicFilter


class FilterTest(unittest.TestCase):

    def test_filter_basic(self):
        f = Filter()
        self.assertEqual(repr(f), '<Filter []>', 'empty filter')
        self.assertEqual(repr(~f), '<Filter []>', '"not" of empty filter')

        # Because the order in listing keys is arbitrary, we only
        # test with one entry.
        f1 = Filter(price='Free')
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

    def test_raw_filters(self):
        # Simple filter
        raw_filter = '[["field_a", "value_a"]]'
        f = Filter(raw_filter)
        self.assertEqual(
            f.filters, [[u'field_a', u'value_a']]
        )
        f = Query._process_filters([f])
        self.assertEqual(
            f, [[u'field_a', u'value_a']]
        )

        # Compounded filter
        raw_filter = '[["field_a", "value_a"], {"not": {"or": ["field_x", "value_x"]}}]'  # noqa
        f = Filter(raw_filter)
        self.assertEqual(
            f.filters, [{'and': [[u'field_a', u'value_a'],
                                 {u'not': {u'or': [u'field_x', u'value_x']}}]}]
        )
        f = Query._process_filters([f])
        self.assertEqual(
            f, [{'and': [[u'field_a', u'value_a'],
                         {u'not': {u'or': [u'field_x', u'value_x']}}]}]
        )

        # Dict-only as list, and not as a list
        raw_filter = '[{"or": [["field_x", "value_x"]]}]'
        f = Filter(raw_filter)
        self.assertEqual(
            f.filters, [{'or': [[u'field_x', u'value_x']]}]
        )
        f = Query._process_filters([f])
        self.assertEqual(
            f, [{'or': [[u'field_x', u'value_x']]}]
        )

        raw_filter = '{"or": [["field_x", "value_x"]]}'
        f = Filter(raw_filter)
        self.assertEqual(
            f.filters, [{'or': [[u'field_x', u'value_x']]}]
        )
        f = Query._process_filters([f])
        self.assertEqual(
            f, [{'or': [[u'field_x', u'value_x']]}]
        )

    def test_combined_raw_filters(self):
        # Combined JSON and regular filter
        raw_filter = '[["field_a", "value_a"]]'
        f = Filter(raw_filter, field_x='value_x')
        self.assertEqual(
            f.filters, [{'and': [('field_x', 'value_x'),
                                 [u'field_a', u'value_a']]}]
        )
        f = Query._process_filters([f])
        self.assertEqual(
            f, [{'and': [('field_x', 'value_x'),
                         [u'field_a', u'value_a']]}]
        )

        # Combined, separate raw filters
        raw_filter = '[["field_a", "value_a"]]'
        f = Filter(raw_filter) | Filter(raw_filter)
        self.assertEqual(
            f.filters, [{'or': [[u'field_a', u'value_a'],
                                [u'field_a', u'value_a']]}]
        )
        f = Query._process_filters([f])
        self.assertEqual(
            f, [{'or': [[u'field_a', u'value_a'],
                        [u'field_a', u'value_a']]}]
        )

        # Combined list of raw filters
        raw_filter = '[["field_a", "value_a"]]'
        f = Filter(raw_filter, raw_filter)
        self.assertEqual(
            f.filters, [{'and': [[u'field_a', u'value_a'],
                                 [u'field_a', u'value_a']]}]
        )
        f = Query._process_filters([f])
        self.assertEqual(
            f, [{'and': [[u'field_a', u'value_a'],
                         [u'field_a', u'value_a']]}]
        )

    def test_process_filters(self):
        filters = [('omim_id', None)]
        self.assertEqual(repr(Query._process_filters(filters)), repr(filters))


class GenomicFilterTest(unittest.TestCase):
    def test_single_position(self):
        f = GenomicFilter('chr1', 100)
        expected = [
            "<GenomicFilter [{'and': [('genomic_coordinates.start__lte', 100), ('genomic_coordinates.stop__gte', 100), ('genomic_coordinates.chromosome', '1')]}]>",  # noqa
            "<GenomicFilter [{'and': [('genomic_coordinates.stop__gte', 100), ('genomic_coordinates.start__lte', 100), ('genomic_coordinates.chromosome', '1')]}]>",  # noqa
        ]
        self.assertTrue(repr(f) in expected)

        f = GenomicFilter('chr1', 100, exact=True)
        expected = [
            "<GenomicFilter [{'and': [('genomic_coordinates.stop', 100), ('genomic_coordinates.start', 100), ('genomic_coordinates.chromosome', '1')]}]>",  # noqa
            "<GenomicFilter [{'and': [('genomic_coordinates.start', 100), ('genomic_coordinates.stop', 100), ('genomic_coordinates.chromosome', '1')]}]>",  # noqa
        ]
        self.assertTrue(repr(f) in expected)  # noqa

    def test_range(self):
        f = GenomicFilter('chr1', 100, 200)
        expected = [
            "<GenomicFilter [{'and': [{'or': [{'and': [('genomic_coordinates.start__lte', 100), ('genomic_coordinates.stop__gte', 200)]}, ('genomic_coordinates.start__range', [100, 200]), ('genomic_coordinates.stop__range', [100, 200])]}, ('genomic_coordinates.chromosome', '1')]}]>",  # noqa
            "<GenomicFilter [{'and': [{'or': [{'and': [('genomic_coordinates.stop__gte', 200), ('genomic_coordinates.start__lte', 100)]}, ('genomic_coordinates.start__range', [100, 200]), ('genomic_coordinates.stop__range', [100, 200])]}, ('genomic_coordinates.chromosome', '1')]}]>",  # noqa
        ]
        if repr(f) not in expected:
            print(repr(f))
        self.assertTrue(repr(f) in expected)

        f = GenomicFilter('chr1', 100, 200, exact=True)
        expected = [
            "<GenomicFilter [{'and': [('genomic_coordinates.stop', 200), ('genomic_coordinates.start', 100), ('genomic_coordinates.chromosome', '1')]}]>",  # noqa
            "<GenomicFilter [{'and': [('genomic_coordinates.start', 100), ('genomic_coordinates.stop', 200), ('genomic_coordinates.chromosome', '1')]}]>",  # noqa
        ]
        if repr(f) not in expected:
            print(repr(f))
        self.assertTrue(repr(f) in expected)


if __name__ == "__main__":
    unittest.main()
