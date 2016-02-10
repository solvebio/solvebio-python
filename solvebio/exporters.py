# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
from collections import OrderedDict

import pyprind

try:
    import unicodecsv as csv
except ImportError:
    import csv

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class Exporters(object):
    """Maintains a list of available exporters."""
    EXPORT_WARN = 5000
    PAGE_SIZE = 500

    registry = {}

    def register(self, klass):
        self.registry[klass.name.lower()] = klass

    def export(self, exporter, query, *args, **kwargs):
        exporter = exporter.lower()
        force = kwargs.pop('force', False)

        if exporter not in self.registry:
            raise Exception('Invalid exporter: {}. Available exporters: {}'
                            .format(exporter, ', '.join(self.registry.keys())))

        nrecords = len(query)
        if nrecords == 0:
            raise Exception('There are no results to export.')
        elif nrecords > self.EXPORT_WARN and not force:
            print('To export {} records, use `force=True`.'
                  .format(nrecords))
            return

        # Increase the efficiency of the export.
        query._page_size = self.PAGE_SIZE
        # Enable progress by default on large exports, but allow toggle.
        show_progress = kwargs.pop('show_progress',
                                   nrecords > self.EXPORT_WARN)
        return self.registry[exporter](query, show_progress=show_progress)\
            .export(*args, **kwargs)


class CSVExporter(object):
    """
    This class includes helper functions to export
    a SolveBio Query object to a CSV file.
    """
    name = 'csv'

    collection = None

    SEP_CHAR = '\r'
    KEY_VAL_CHAR = ': '
    DICT_SEP_CHAR = '\r'
    DICT_OPEN = ''
    DICT_CLOSE = ''

    def __init__(self, query, *args, **kwargs):
        self.query = query
        self.show_progress = kwargs.get('show_progress', False)

    def export(self, filename=None, **kwargs):
        if not filename:
            raise Exception(
                'The "filename" parameter is required to export.')

        filename = os.path.expanduser(filename)

        from solvebio import Dataset

        result_count = len(self.query)
        if result_count <= 0:
            raise AttributeError('No results found in query!')

        self.rows = []
        self.key_map = OrderedDict()
        self.key_types = {}

        for f in Dataset.retrieve(self.query._dataset_id).fields(limit=1000):
            name = f['name']
            splits = [int(s) if s.isdigit() else s
                      for s in name.split('.')]
            self.key_map[name] = splits
            self.key_types[name] = f['data_type']

        title = 'Exporting query to: {}'.format(filename)

        if self.show_progress:
            progress_bar = pyprind.ProgPercent(
                result_count,
                title=title,
                track_time=False)
        else:
            print(title)

        for ind, record in enumerate(self.query):
            row = self.process_record(record)
            self.rows.append(row)
            if self.show_progress:
                progress_bar.update()

        self.write(filename=filename)
        print('Export complete!')

    def process_cell(self, keys, cell):
        if not keys:
            return [cell]
        elif not cell:
            return []

        # Retrieve the cell values for a nested dict.
        for i, k in enumerate(keys):
            if isinstance(cell, list):
                return [self.process_cell(keys[i:], c)
                        for c in cell]
            elif isinstance(cell, dict):
                return self.process_cell(keys[i + 1:], cell.get(k))
            elif i == len(keys) - 1:
                # Last key, return the cell
                return []

    def process_record(self, record):
        """Process a row of json data against the key map
        """
        row = {}

        for header, keys in self.key_map.items():
            try:
                cells = self.process_cell(keys, record)
            except (KeyError, IndexError, TypeError):
                cells = []

            row[header] = self.SEP_CHAR.join(
                [self.make_string(cell) for cell in cells])

        return row

    def make_string(self, item):
        if isinstance(item, list) or \
                isinstance(item, set) or \
                isinstance(item, tuple):
            return self.SEP_CHAR.join(
                [self.make_string(subitem) for subitem in item])
        elif isinstance(item, dict):
            return self.DICT_OPEN + self.DICT_SEP_CHAR.join(
                [self.KEY_VAL_CHAR.join(
                    [k, self.make_string(val)]
                ) for k, val in item.items()]
            ) + self.DICT_CLOSE
        elif item:
            return str(item).strip()
        else:
            return ''

    def write(self, filename):
        if sys.version_info >= (3, 0, 0):
            f = open(filename, 'w', newline='')
        else:
            f = open(filename, 'wb')

        try:
            writer = csv.DictWriter(f, self.key_map.keys())
            writer.writeheader()
            writer.writerows(self.rows)
        except:
            raise
        finally:
            f.close()


class XLSXExporter(CSVExporter):
    """Uses XlsxWriter to export a valid XLS."""

    name = 'excel'

    SEP_CHAR = '\n'
    KEY_VAL_CHAR = ': '
    DICT_SEP_CHAR = '\n'
    DICT_OPEN = ''
    DICT_CLOSE = ''

    NUMERIC_TYPES = ('integer', 'double', 'long', 'float')

    def __init__(self, query, *args, **kwargs):
        if not xlsxwriter:
            raise Exception(
                'The XLSX exporter requires the xlsxwriter Python module. '
                'Run `pip install XlsxWriter` and reload SolveBio.')

        self.query = query
        self.show_progress = kwargs.get('show_progress', False)

    def write(self, filename):
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()
        formats = {
            'text': workbook.add_format({'text_wrap': True}),
            'string': workbook.add_format(),
            'header': workbook.add_format({'bold': True}),
            'integer': workbook.add_format(),
            'double': workbook.add_format(),
            'long': workbook.add_format(),
            'float': workbook.add_format(),
        }
        formats['date'] = formats['string']
        formats['boolean'] = formats['string']

        formats['text'].set_align('top')
        formats['nested'] = formats['text']
        formats['object'] = formats['text']

        row = 0
        # Write the header
        for col, k in enumerate(self.key_map.keys()):
            worksheet.write(row, col, k, formats['header'])

        for record in self.rows:
            row += 1
            for col, k in enumerate(sorted(record)):
                fmt = formats.get(self.key_types[k], formats['text'])
                if self.key_types[k] in self.NUMERIC_TYPES:
                    from decimal import Decimal
                    try:
                        val = Decimal(record[k])
                        worksheet.write_number(row, col, val, fmt)
                    except:
                        # Might be multi-line numeric.
                        worksheet.write(row, col, record[k], fmt)
                else:
                    worksheet.write(row, col, record[k].encode('utf-8'), fmt)

        workbook.close()


exporters = Exporters()
exporters.register(CSVExporter)
exporters.register(XLSXExporter)
