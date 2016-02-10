# -*- coding: utf-8 -*-
from __future__ import print_function
from six import u

import os
import sys
from collections import OrderedDict

import pyprind

try:
    import unicodecsv as csv
except ImportError:
    import csv


class Exporters(object):
    """Maintains a list of available exporters."""
    EXPORT_WARN = 5000
    PAGE_SIZE = 500

    registry = {}

    def register(self, klass):
        if klass.is_available():
            self.registry[klass.name] = klass

    def export(self, exporter, query, *args, **kwargs):
        force = kwargs.pop('force', False)

        if exporter in self.registry:
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
        else:
            raise Exception('Invalid exporter: {}. Available exporters: {}'
                            .format(exporter, ', '.join(self.registry.keys())))


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

    @classmethod
    def is_available(cls):
        return True

    def export(self, filename=None, **kwargs):
        if not filename:
            raise Exception(
                '"filename" is a required parameter '
                'for the CSV exporter.')

        filename = os.path.expanduser(filename)

        from solvebio import Dataset

        result_count = len(self.query)
        if result_count <= 0:
            raise AttributeError('No results found in query!')

        self.rows = []
        self.key_map = OrderedDict()

        for f in Dataset.retrieve(self.query._dataset_id).fields(limit=1000):
            name = f['name']
            splits = [int(s) if s.isdigit() else s
                      for s in name.split('.')]
            self.key_map[name] = splits

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

        self.write_csv(filename=filename)
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
            return u(str(item)).strip()
        else:
            return ''

    def write_csv(self, filename):
        """Write the processed rows to the given filename
        """
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

exporters = Exporters()
exporters.register(CSVExporter)
