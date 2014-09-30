#!/usr/bin/env python
# -*- coding: utf-8 -*-
import solvebio
import unittest
from solvebio.utils import tabulate as t
from solvebio.utils import printing as p

class TestTabulate(unittest.TestCase):

    def test_classify(self):

        self.assertEqual(t._isnumber('123.45'), True)
        self.assertEqual(t._isnumber('123'),    True)
        self.assertEqual(t._isnumber('spam'),   False)
        self.assertEqual(t._isint('123'),       True)
        self.assertEqual(t._isint('123.45'),    False)

        self.assertEqual(t._type(None),   t._none_type)
        self.assertEqual(t._type(u'foo'), t._text_type)
        self.assertEqual(t._type('1'),    t._int_type)
        self.assertEqual(t._type(1),      t._int_type)
        self.assertEqual(t._type('\x1b[31m42\x1b[0m'), t._int_type)

    def test_align(self):
        self.assertEqual(t._afterpoint('123.45'),  2)
        self.assertEqual(t._afterpoint('1001'),   -1)

        self.assertEqual(t._afterpoint('eggs'),   -1)
        self.assertEqual(t._afterpoint('123e45'),  2)

        self.assertEqual(t._padleft(6, u'abcd'),  u'  abcd')
        self.assertEqual(t._padright(6, u"abcd"), u"abcd  ")

        self.assertEqual(t._padboth(6, "abcd"), " abcd ")

        self.assertEqual(t._padboth(7, "abcd"), " abcd  ")

        self.assertEqual(t._padright(2, 'abc'), 'abc')
        self.assertEqual(t._padleft(2,  'abc'), 'abc')
        self.assertEqual(t._padboth(2,  'abc'), 'abc')


        self.assertEqual(
            t._align_column(
                ["12.345", "-1234.5", "1.23", "1234.5",
                 "1e+234", "1.0e234"], "decimal"),
                 ['   12.345  ', '-1234.5    ', '    1.23   ',
                      ' 1234.5    ', '    1e+234 ', '    1.0e234'])

    def test_column_type(self):
        self.assertEqual(t._column_type(["1", "2"]), t._int_type)
        self.assertEqual(t._column_type(["1", "2.3"]), t._float_type)
        self.assertEqual(t._column_type(["1", "2.3", "four"]), t._text_type)
        self.assertEqual(t._column_type(["four", u'\u043f\u044f\u0442\u044c']),
                         t._text_type)

        self.assertEqual(t._column_type([None, "brux"]), t._text_type)
        self.assertEqual(t._column_type([1, 2, None]), t._int_type)

    def test_tabulate(self):
        tsv = t.simple_separated_format("\t")
        p.TTY_COLS = 80
        expected = """foo 	 1
spam\t23
"""
        self.assertEqual(t.tabulate([["foo", 1], ["spam", 23]], [], tsv), expected[0:-1],
                         'simple separated format table')
        ####################################################################

#         expected = """a|         |         |
# |---------+---------|
# |         |       2 |
# |         |       4 |
# """
#         hrow = [u'\u0431\u0443\u043a\u0432\u0430', u'\u0446\u0438\u0444\u0440\u0430']
#         tbl = [[u"\u0430\u0437", 2], ["\u0431\u0443\u043a\u0438", 4]]

#         print
#         x = t.tabulate(tbl, hrow)
#         print x
#         print expected
#         print len(expected)-1, len(x)
#         for i in range(len(expected)-1):
#             print "'%s' '%s' %s" % (x[i], expected[i], x[i] == expected[i])


#         self.assertEqual(expected[1:-1], t.tabulate(tbl, hrow),
#                      'org mode with header and unicode')

        ###################################################################

#         expected = """| Fields                | Data                        |
# |-----------------------+-----------------------------|
# | rcvaccession_version  | 2                           |
# | hg18_chromosome       | 3                           |
# | hg19_start            | 148562304                   |
# | rcvaccession          | RCV000060731                |
# | hg38_start            | 148844517                   |
# | reference_allele      | C                           |
# | gene_symbols          | CPB1                        |
# | rsid                  | rs150241322                 |
# | hg19_chromosome       | 3                           |
# | hgvs                  | NC_000003.12:g.148844517C>T |
# | clinical_significance | other                       |
# | alternate_alleles     | T                           |
# | clinical_origin       | somatic                     |
# | type                  | SNV                         |
# """

#         hash = {
#             "rcvaccession_version":2,
#             "hg18_chromosome":"3",
#             "hg19_start":148562304,
#             "rcvaccession":"RCV000060731",
#             "hg38_start":148844517,
#             "reference_allele":"C",
#             "gene_symbols":["CPB1"],
#             "rsid":"rs150241322",
#             "hg19_chromosome":"3",
#             "hgvs":["NC_000003.12:g.148844517C>T"],
#             "clinical_significance":"other",
#             "alternate_alleles":["T"],
#             "clinical_origin":["somatic"],
#             "type":"SNV"
#         }
#         self.assertEqual(t.tabulate(hash,
#                                     headers=('Fields', 'Data'),
#                                     aligns= ('right', 'left')),
#                                     expected[0:-1],
#                                     'mixed data with arrays; close to actual query output')

if __name__ == "__main__":
    unittest.main()
