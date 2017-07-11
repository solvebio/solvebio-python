# -*- coding: utf-8 -*-
#
# This file contains code from python-tabulate, modified for SolveBio
#
# Copyright © 2011-2013 Sergey Astanin
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
from __future__ import print_function
from __future__ import absolute_import

from six.moves import map
from six.moves import range
from six.moves import zip
from six import string_types

from collections import namedtuple
from platform import python_version_tuple
import re
from .printing import TTY_COLS

if python_version_tuple()[0] < "3":
    from itertools import izip_longest
    _none_type = type(None)
    _int_type = int
    _float_type = float
    _text_type = str
    _binary_type = str
else:
    from itertools import zip_longest as izip_longest
    from functools import reduce
    _none_type = type(None)
    _int_type = int
    _float_type = float
    _text_type = str
    _binary_type = bytes


__all__ = ["tabulate"]
__version__ = "0.6"


Line = namedtuple("Line", ["begin", "hline", "sep", "end"])
DataRow = namedtuple("DataRow", ["begin", "sep", "end"])
TableFormat = namedtuple("TableFormat", ["lineabove", "linebelowheader",
                                         "linebetweenrows", "linebelow",
                                         "headerrow", "datarow",
                                         "padding", "usecolons",
                                         "with_header_hide",
                                         "without_header_hide"])
_format_defaults = {"padding": 0,
                    "usecolons": False,
                    "with_header_hide": [],
                    "without_header_hide": []}

_table_formats = {"simple":
                  TableFormat(lineabove=None,
                              linebelowheader=Line("", "-", "  ", ""),
                              linebetweenrows=None,
                              linebelow=Line("", "-", "  ", ""),
                              headerrow=DataRow("", "  ", ""),
                              datarow=DataRow("", "  ", ""),
                              padding=0,
                              usecolons=False,
                              with_header_hide=["linebelow"],
                              without_header_hide=[]),
                  "plain":
                  TableFormat(None, None, None, None,
                              DataRow("", "  ", ""), DataRow("", "  ", ""),
                              **_format_defaults),
                  "grid":
                  TableFormat(lineabove=Line("+", "-", "+", "+"),
                              linebelowheader=Line("+", "=", "+", "+"),
                              linebetweenrows=Line("+", "-", "+", "+"),
                              linebelow=Line("+", "-", "+", "+"),
                              headerrow=DataRow("|", "|", "|"),
                              datarow=DataRow("|", "|", "|"),
                              padding=1,
                              usecolons=False,
                              with_header_hide=[],
                              without_header_hide=["linebelowheader"]),
                  "pipe":
                  TableFormat(lineabove=None,
                              linebelowheader=Line("|", "-", "|", "|"),
                              linebetweenrows=None,
                              linebelow=None,
                              headerrow=DataRow("|", "|", "|"),
                              datarow=DataRow("|", "|", "|"),
                              padding=1,
                              usecolons=True,
                              with_header_hide=[],
                              without_header_hide=[]),
                  "orgmode":
                  TableFormat(lineabove=None,
                              linebelowheader=Line("|", "-", "+", "|"),
                              linebetweenrows=None,
                              linebelow=None,
                              headerrow=DataRow("|", "|", "|"),
                              datarow=DataRow("|", "|", "|"),
                              padding=1,
                              usecolons=False,
                              with_header_hide=[],
                              without_header_hide=["linebelowheader"])}


_invisible_codes = re.compile(r'\x1b\[\d*m')  # ANSI color codes


def simple_separated_format(separator):
    """
    Construct a simple TableFormat with columns separated by a separator.

    >>> tsv = simple_separated_format("\t") ; \
        tabulate([["foo", 1], ["spam", 23]], \
            tablefmt=tsv) == 'foo \\t 1\\nspam\\t23'
    True

    """
    return TableFormat(None, None, None, None,
                       headerrow=None, datarow=DataRow('', separator, ''),
                       **_format_defaults)


def _isconvertible(conv, string):
    try:
        conv(string)  # noqa
        return True
    except (TypeError, ValueError):
        return False


def _isnumber(string):
    """
    >>> _isnumber("123.45")
    True
    >>> _isnumber("123")
    True
    >>> _isnumber("spam")
    False
    """
    return _isconvertible(float, string)


def _isint(string):
    """
    >>> _isint("123")
    True
    >>> _isint("123.45")
    False
    """
    return type(string) is int or \
        (isinstance(string, _binary_type) or
         isinstance(string, string_types)) and \
        _isconvertible(int, string)


def _type(string, has_invisible=True):
    """
    The least generic type (type(None), int, float, str, unicode).

    >>> _type(None) is type(None)
    True
    >>> _type("foo") is type("")
    True
    >>> _type("1") is type(1)
    True
    >>> _type('\x1b[31m42\x1b[0m') is type(42)
    True
    >>> _type('\x1b[31m42\x1b[0m') is type(42)
    True

    """

    if has_invisible and \
       (isinstance(string, _text_type) or isinstance(string, _binary_type)):
        string = _strip_invisible(string)

    if string is None:
        return _none_type
    elif _isint(string):
        return _int_type
    elif _isnumber(string):
        return float
    elif isinstance(string, _binary_type):
        return _binary_type
    else:
        return _text_type


def _afterpoint(string):
    """
    Symbols after a decimal point, -1 if the string lacks the decimal point.

    >>> _afterpoint("123.45")
    2
    >>> _afterpoint("1001")
    -1
    >>> _afterpoint("eggs")
    -1
    >>> _afterpoint("123e45")
    2

    """
    if _isnumber(string):
        if _isint(string):
            return -1
        else:
            pos = string.rfind(".")
            pos = string.lower().rfind("e") if pos < 0 else pos
            if pos >= 0:
                return len(string) - pos - 1
            else:
                return -1  # no point
    else:
        return -1  # not a number


def _padleft(width, s, has_invisible=True):
    """
    Flush right.

    >>> _padleft(6, '\u044f\u0439\u0446\u0430') \
        == '  \u044f\u0439\u0446\u0430'
    True

    """
    iwidth = width + len(s) - len(_strip_invisible(s)) \
        if has_invisible else width
    fmt = "{0:>%ds}" % iwidth
    return fmt.format(s)


def _padright(width, s, has_invisible=True):
    """
    Flush left.

    >>> _padright(6, '\u044f\u0439\u0446\u0430') \
        == '\u044f\u0439\u0446\u0430  '
    True

    """
    iwidth = width + len(s) - len(_strip_invisible(s)) \
        if has_invisible else width
    fmt = "{0:<%ds}" % iwidth
    return fmt.format(s)


def _padboth(width, s, has_invisible=True):
    """
    Center string.

    >>> _padboth(6, '\u044f\u0439\u0446\u0430') \
        == ' \u044f\u0439\u0446\u0430 '
    True

    """
    iwidth = width + len(s) - len(_strip_invisible(s)) \
        if has_invisible else width
    fmt = "{0:^%ds}" % iwidth
    return fmt.format(s)


def _strip_invisible(s):
    "Remove invisible ANSI color codes."
    return re.sub(_invisible_codes, "", s)


def _visible_width(s):
    """
    Visible width of a printed string. ANSI color codes are removed.

    >>> _visible_width('\x1b[31mhello\x1b[0m'), _visible_width("world")
    (5, 5)

    """
    if isinstance(s, _text_type) or isinstance(s, _binary_type):
        return len(_strip_invisible(s))
    else:
        return len(_text_type(s))


def _align_column(strings, alignment, minwidth=0, has_invisible=True):
    """
    [string] -> [padded_string]

    >>> list(map(str,_align_column( \
        ["12.345", "-1234.5", "1.23", "1234.5", \
         "1e+234", "1.0e234"], "decimal")))
    ['   12.345  ', '-1234.5    ', '    1.23   ', \
     ' 1234.5    ', '    1e+234 ', '    1.0e234']

    """
    if alignment == "right":
        strings = [s.strip() for s in strings]
        padfn = _padleft
    elif alignment in "center":
        strings = [s.strip() for s in strings]
        padfn = _padboth
    elif alignment in "decimal":
        decimals = [_afterpoint(s) for s in strings]
        maxdecimals = max(decimals)
        strings = [s + (maxdecimals - decs) * " "
                   for s, decs in zip(strings, decimals)]
        padfn = _padleft
    else:
        strings = [s.strip() for s in strings]
        padfn = _padright

    if has_invisible:
        width_fn = _visible_width
    else:
        width_fn = len

    maxwidth = max(max(list(map(width_fn, strings))), minwidth)
    padded_strings = [padfn(maxwidth, s, has_invisible) for s in strings]
    return padded_strings


def _more_generic(type1, type2):
    types = {_none_type: 0, int: 1, float: 2, _text_type: 4}
    invtypes = {4: _text_type, 2: float, 1: int, 0: _none_type}
    moregeneric = max(types.get(type1, 4), types.get(type2, 4))
    return invtypes[moregeneric]


def _column_type(strings, has_invisible=True):
    """
    The least generic type all column values are convertible to.

    >>> _column_type(["1", "2"]) is _int_type
    True
    >>> _column_type(["1", "2.3"]) is _float_type
    True
    >>> _column_type(["1", "2.3", "four"]) is _text_type
    True
    >>> _column_type(["four", '\u043f\u044f\u0442\u044c']) is _text_type
    True
    >>> _column_type([None, "brux"]) is _text_type
    True
    >>> _column_type([1, 2, None]) is _int_type
    True

    """
    types = [_type(s, has_invisible) for s in strings]
    return reduce(_more_generic, types, int)


def _format(val, valtype, floatfmt, missingval=""):
    """
    Format a value accoding to its type.

    Unicode is supported:

    >>> hrow = ['\u0431\u0443\u043a\u0432\u0430', \
                '\u0446\u0438\u0444\u0440\u0430'] ; \
        tbl = [['\u0430\u0437', 2], ['\u0431\u0443\u043a\u0438', 4]] ; \
        good_result = '\\u0431\\u0443\\u043a\\u0432\\u0430      \
                        \\u0446\\u0438\\u0444\\u0440\\u0430\\n-------\
                          -------\\n\\u0430\\u0437             \
                          2\\n\\u0431\\u0443\\u043a\\u0438           4' ; \
        tabulate(tbl, headers=hrow) == good_result
    True

    """
    if val is None:
        return missingval

    if valtype in [int, _binary_type, _text_type]:
        return "{0}".format(val)
    elif valtype is float:
        return format(float(val), floatfmt)
    else:
        return "{0}".format(val)


def _align_header(header, alignment, width):
    if alignment == "left":
        return _padright(width, header)
    elif alignment == "center":
        return _padboth(width, header)
    else:
        return _padleft(width, header)


def _normalize_tabular_data(tabular_data, headers, sort=True):
    """
    Transform a supported data type to a list of lists, and a list of headers.

    Supported tabular data types:

    * list-of-lists or another iterable of iterables

    * 2D NumPy arrays

    * dict of iterables (usually used with headers="keys")

    * pandas.DataFrame (usually used with headers="keys")

    The first row can be used as headers if headers="firstrow",
    column indices can be used as headers if headers="keys".

    """

    if hasattr(tabular_data, "keys") and hasattr(tabular_data, "values"):
        # dict-like and pandas.DataFrame?
        if hasattr(tabular_data.values, "__call__"):
            # likely a conventional dict
            keys = list(tabular_data.keys())
            # columns have to be transposed
            rows = list(izip_longest(*list(tabular_data.values())))
        elif hasattr(tabular_data, "index"):
            # values is a property, has .index then
            # it's likely a pandas.DataFrame (pandas 0.11.0)
            keys = list(tabular_data.keys())
            # values matrix doesn't need to be transposed
            vals = tabular_data.values
            names = tabular_data.index
            rows = [[v] + list(row) for v, row in zip(names, vals)]
        else:
            raise ValueError("tabular data doesn't appear to be a dict "
                             "or a DataFrame")

        if headers == "keys":
            headers = list(map(_text_type, keys))  # headers should be strings

    else:  # it's, as usual, an iterable of iterables, or a NumPy array
        rows = list(tabular_data)

        if headers == "keys" and len(rows) > 0:  # keys are column indices
            headers = list(map(_text_type, list(range(len(rows[0])))))

    # take headers from the first row if necessary
    if headers == "firstrow" and len(rows) > 0:
        headers = list(map(_text_type, rows[0]))  # headers should be strings
        rows = rows[1:]

    headers = list(headers)

    rows = list(map(list, rows))

    if sort and len(rows) > 1:
        rows = sorted(rows, key=lambda x: x[0])

    # pad with empty headers for initial columns if necessary
    if headers and len(rows) > 0:
        nhs = len(headers)
        ncols = len(rows[0])
        if nhs < ncols:
            headers = [""] * (ncols - nhs) + headers

    return rows, headers


def _build_row(cells, padding, begin, sep, end):
    "Return a string which represents a row of data cells."

    pad = " " * padding
    padded_cells = [pad + cell + pad for cell in cells]

    # SolveBio: we're only displaying Key-Value tuples (dimension of 2).
    #  enforce that we don't wrap lines by setting a max
    #  limit on row width which is equal to TTY_COLS (see printing)
    rendered_cells = (begin + sep.join(padded_cells) + end).rstrip()
    if len(rendered_cells) > TTY_COLS:
        if not cells[-1].endswith(" ") and not cells[-1].endswith("-"):
            terminating_str = " ... "
        else:
            terminating_str = ""
        rendered_cells = "{0}{1}{2}".format(
            rendered_cells[:TTY_COLS - len(terminating_str) - 1],
            terminating_str, end)

    return rendered_cells


def _build_line(colwidths, padding, begin, fill, sep, end):
    "Return a string which represents a horizontal line."
    cells = [fill * (w + 2 * padding) for w in colwidths]
    return _build_row(cells, 0, begin, sep, end)


def _mediawiki_cell_attrs(row, colaligns):
    "Prefix every cell in a row with an HTML alignment attribute."
    alignment = {"left": '',
                 "right": 'align="right"| ',
                 "center": 'align="center"| ',
                 "decimal": 'align="right"| '}
    row2 = [alignment[a] + c for c, a in zip(row, colaligns)]
    return row2


def _line_segment_with_colons(linefmt, align, colwidth):
    """Return a segment of a horizontal line with optional colons which
    indicate column's alignment (as in `pipe` output format)."""
    fill = linefmt.hline
    w = colwidth
    if align in ["right", "decimal"]:
        return (fill[0] * (w - 1)) + ":"
    elif align == "center":
        return ":" + (fill[0] * (w - 2)) + ":"
    elif align == "left":
        return ":" + (fill[0] * (w - 1))
    else:
        return fill[0] * w


def _format_table(fmt, headers, rows, colwidths, colaligns):
    """Produce a plain-text representation of the table."""
    lines = []
    hidden = fmt.with_header_hide if headers else fmt.without_header_hide
    pad = fmt.padding
    headerrow = fmt.headerrow if fmt.headerrow else fmt.datarow

    if fmt.lineabove and "lineabove" not in hidden:
        lines.append(_build_line(colwidths, pad, *fmt.lineabove))

    if headers:
        lines.append(_build_row(headers, pad, *headerrow))

    if fmt.linebelowheader and "linebelowheader" not in hidden:
        begin, fill, sep, end = fmt.linebelowheader
        if fmt.usecolons:
            segs = [
                _line_segment_with_colons(fmt.linebelowheader, a, w + 2 * pad)
                for w, a in zip(colwidths, colaligns)]
            lines.append(_build_row(segs, 0, begin, sep, end))
        else:
            lines.append(_build_line(colwidths, pad, *fmt.linebelowheader))

    if rows and fmt.linebetweenrows and "linebetweenrows" not in hidden:
        # initial rows with a line below
        for row in rows[:-1]:
            lines.append(_build_row(row, pad, *fmt.datarow))
            lines.append(_build_line(colwidths, pad, *fmt.linebetweenrows))
        # the last row without a line below
        lines.append(_build_row(rows[-1], pad, *fmt.datarow))
    else:
        for row in rows:
            lines.append(_build_row(row, pad, *fmt.datarow))

    if fmt.linebelow and "linebelow" not in hidden:
        lines.append(_build_line(colwidths, pad, *fmt.linebelow))

    return "\n".join(lines)


def tabulate(tabular_data, headers=[], tablefmt="orgmode",
             floatfmt="g", aligns=[], missingval="", sort=True):
    list_of_lists, headers = _normalize_tabular_data(tabular_data, headers,
                                                     sort=sort)

    # optimization: look for ANSI control codes once,
    # enable smart width functions only if a control code is found
    plain_text = '\n'.join(
        ['\t'.join(map(_text_type, headers))] +
        ['\t'.join(map(_text_type, row)) for row in list_of_lists])

    has_invisible = re.search(_invisible_codes, plain_text)
    if has_invisible:
        width_fn = _visible_width
    else:
        width_fn = len

    # format rows and columns, convert numeric values to strings
    cols = list(zip(*list_of_lists))

    coltypes = list(map(_column_type, cols))
    cols = [[_format(v, ct, floatfmt, missingval) for v in c]
            for c, ct in zip(cols, coltypes)]

    # align columns
    if not aligns:
        # dynamic alignment by col type
        aligns = ["decimal" if ct in [int, float] else "left"
                  for ct in coltypes]

    minwidths = [width_fn(h) + 2 for h in headers] if headers \
        else [0] * len(cols)
    cols = [_align_column(c, a, minw, has_invisible)
            for c, a, minw in zip(cols, aligns, minwidths)]

    if headers:
        # align headers and add headers
        minwidths = [max(minw, width_fn(c[0]))
                     for minw, c in zip(minwidths, cols)]
        headers = [_align_header(h, a, minw)
                   for h, a, minw in zip(headers, aligns, minwidths)]
    else:
        minwidths = [width_fn(c[0]) for c in cols]
    rows = list(zip(*cols))

    if not isinstance(tablefmt, TableFormat):
        tablefmt = _table_formats.get(tablefmt, _table_formats["orgmode"])

    # make sure values don't have newlines or tabs in them
    rows = [[str(c).replace('\n', '').replace('\t', '').replace('\r', '')
            for c in r] for r in rows]
    return _format_table(tablefmt, headers, rows, minwidths, aligns)


if __name__ == "__main__":
    data = [
        ("gene_symbols", ["CPB1"]),
        ("clinical_significance", "other"),
        ("clinical_origin", ["somatic"]),
        ("alternate_alleles", ["T"]), ]
    print(tabulate(data,
                   headers=('Fields', 'Data'),
                   aligns=('right', 'left'), sort=True))
    print(tabulate(data,
                   headers=('Fields', 'Data'),
                   aligns=('right', 'left'), sort=False))
