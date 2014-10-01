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

        expected = """| abcd   |   12345 |
|--------+---------|
| XY     |       2 |
| lmno   |       4 |
"""
        hrow = [u'abcd', u'12345']
        tbl = [[u"XY", 2], ["lmno", 4]]

        self.assertEqual(t.tabulate(tbl, hrow), expected[0:-1],
                     'org mode with header and unicode')

        ###################################################################

        expected = """|                Fields | Data                            |
|-----------------------+---------------------------------|
|            hg19_start | 148562304                       |
|          rcvaccession | RCV000060731                    |
|            hg38_start | 148844517                       |
|          gene_symbols | ['CPB1']                        |
|     alternate_alleles | ['T']                           |
|       clinical_origin | ['somatic']                     |
|       hg18_chromosome | 3                               |
|  rcvaccession_version | 2                               |
|      reference_allele | C                               |
|                  rsid | rs150241322                     |
|       hg19_chromosome | 3                               |
|                  hgvs | ['NC_000003.12:g.148844517C>T'] |
| clinical_significance | other                           |
|                  type | SNV                             |
"""
        h = {
           "rcvaccession_version":2,
           "hg18_chromosome":"3",
           "hg19_start":148562304,
           "rcvaccession":"RCV000060731",
           "hg38_start":148844517,
           "reference_allele":"C",
           "gene_symbols":["CPB1"],
           "rsid":"rs150241322",
           "hg19_chromosome":"3",
           "hgvs":["NC_000003.12:g.148844517C>T"],
           "clinical_significance":"other",
           "alternate_alleles":["T"],
           "clinical_origin":["somatic"],
           "type":"SNV"
        }
        data = t.tabulate(h.items(),
                          headers=('Fields', 'Data'),
                          aligns= ('right', 'left'))

        self.assertEqual(expected[0:-1], data,
                         'mixed data with arrays; close to actual query output')

if __name__ == "__main__":
    unittest.main()
