# -*- coding: utf-8 -*-
from __future__ import absolute_import

import unittest
from solvebio.utils import tabulate as t
from solvebio.utils import printing as p


class TestTabulate(unittest.TestCase):

    def test_classify(self):

        self.assertEqual(t._isnumber('123.45'), True)
        self.assertEqual(t._isnumber('123'), True)
        self.assertEqual(t._isnumber('spam'), False)
        self.assertEqual(t._isint('123'), True)
        self.assertEqual(t._isint('123.45'), False)

        self.assertEqual(t._type(None), t._none_type)
        self.assertEqual(t._type('foo'), t._text_type)
        self.assertEqual(t._type('1'), t._int_type)
        self.assertEqual(t._type(1), t._int_type)
        self.assertEqual(t._type('\x1b[31m42\x1b[0m'), t._int_type)

    def test_align(self):
        self.assertEqual(t._afterpoint('123.45'), 2)
        self.assertEqual(t._afterpoint('1001'), -1)

        self.assertEqual(t._afterpoint('eggs'), -1)
        self.assertEqual(t._afterpoint('123e45'), 2)

        self.assertEqual(t._padleft(6, 'abcd'), '  abcd')
        self.assertEqual(t._padright(6, "abcd"), "abcd  ")

        self.assertEqual(t._padboth(6, "abcd"), " abcd ")

        self.assertEqual(t._padboth(7, "abcd"), " abcd  ")

        self.assertEqual(t._padright(2, 'abc'), 'abc')
        self.assertEqual(t._padleft(2, 'abc'), 'abc')
        self.assertEqual(t._padboth(2, 'abc'), 'abc')

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
        self.assertEqual(t._column_type(["four", '\u043f\u044f\u0442\u044c']),
                         t._text_type)

        self.assertEqual(t._column_type([None, "brux"]), t._text_type)
        self.assertEqual(t._column_type([1, 2, None]), t._int_type)

    def test_tabulate(self):
        p.TTY_COLS = 80
        tsv = t.simple_separated_format("\t")
        expected = """
foo 	 1
spam\t23
"""
        # [-1:1] below to remove leading and trailing "\n"s above
        got = t.tabulate([["foo", 1], ["spam", 23]], [], tsv)
        self.assertEqual(got, expected[1:-1],
                         'simple separated format table')
        ####################################################################

        expected = """
| abcd   |   12345 |
|--------+---------|
| XY     |       2 |
| lmno   |       4 |
"""
        hrow = ['abcd', '12345']
        tbl = [["XY", 2], ["lmno", 4]]

        # [-1:1] below to remove leading and trailing "\n"s above
        self.assertEqual(t.tabulate(tbl, hrow), expected[1:-1],
                         'org mode with header and unicode')

        ###################################################################

        expected = """
|                Fields | Data        |
|-----------------------+-------------|
|     alternate_alleles | ['T']       |
|       clinical_origin | ['somatic'] |
| clinical_significance | other       |
|          gene_symbols | ['CPB1']    |
"""
        data = [
            ("gene_symbols", ["CPB1"]),
            ("clinical_significance", "other"),
            ("clinical_origin", ["somatic"]),
            ("alternate_alleles", ["T"]), ]
        got = t.tabulate(data,
                         headers=('Fields', 'Data'),
                         aligns=('right', 'left'), sort=True)

        # [-1:1] below to remove leading and trailing "\n"s above
        self.assertEqual(got, expected[1:-1],
                         'mixed data with arrays; close to actual ' +
                         'query output')

        expected = """
|                Fields | Data        |
|-----------------------+-------------|
|          gene_symbols | ['CPB1']    |
| clinical_significance | other       |
|       clinical_origin | ['somatic'] |
|     alternate_alleles | ['T']       |
"""
        got = t.tabulate(data,
                         headers=('Fields', 'Data'),
                         aligns=('right', 'left'), sort=False)
        self.assertEqual(got, expected[1:-1],
                         'mixed data with arrays; unsorted')


if __name__ == "__main__":
    unittest.main()
