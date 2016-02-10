# -*- coding: utf-8 -*-
from __future__ import print_function
from six.moves import input
from six.moves import reduce
from six import u

import sys
import operator
from collections import OrderedDict

# try:
#     import pandas
# except ImportError:
#     pandas = None

try:
    import unicodecsv as csv
except ImportError:
    import csv


class Exporter(object):
    """Maintains a list of available exporters."""
    EXPORT_WARN = 10000
    PAGE_SIZE = 1000

    registry = {}

    def register(self, klass):
        x = klass()
        if x.is_available():
            self.registry[x.name] = klass

    def export(self, exporter, query, *args, **kwargs):
        if exporter in self.registry:
            nrecords = len(query)
            if nrecords == 0:
                raise Exception('There are no results to export.')
            elif nrecords > self.EXPORT_WARN:
                print('You have requested an export of more than {} records. '
                      'This may take a while.'.format(nrecords))
                yes = input('Type "yes" to continue exporting: ')
                if yes != 'yes':
                    print('Aborting export!')
                    return

            query._page_size = self.PAGE_SIZE
            return self.registry[exporter]().export(query, *args, **kwargs)
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

    # SEP_CHAR also works as a ', '
    SEP_CHAR = '\r'
    KEY_VAL_CHAR = ': '
    DICT_SEP_CHAR = '\r'
    DICT_OPEN = ''
    DICT_CLOSE = ''

    @classmethod
    def is_available(cls):
        return True

    def export(self, query, filename=None, **kwargs):
        if not filename:
            raise Exception(
                '"filename" is a required parameter '
                'for the CSV exporter.')

        from solvebio import Dataset

        if len(query) <= 0:
            raise AttributeError('No results found in query!')

        self.rows = []
        self.key_map = OrderedDict()

        for f in Dataset.retrieve(query._dataset_id).fields():
            name = f['name']
            splits = [int(s) if s.isdigit() else s
                      for s in name.split('.')]
            self.key_map[name] = splits

        for record in query:
            row = self.process_record(record)
            self.rows.append(row)

        self.write_csv(filename=filename)

    def process_record(self, record):
        """Process a row of json data against the key map
        """
        row = {}

        for header, keys in self.key_map.items():
            try:
                row[header] = reduce(operator.getitem, keys, record)
            except (KeyError, IndexError, TypeError):
                row[header] = None

        row = {k: self.make_string(val)
               for k, val in row.items()}

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
            return u(str(item))
        else:
            return u('')

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


# class PandasExporter(object):
#     """
#     This class includes helper functions to change data
#     formats between SolveBio Queries and Pandas DataFrames.
#     For more information visit http://pandas.pydata.org.
#     """
#     name = 'pandas'
#
#     @classmethod
#     def is_available(cls):
#         return bool(pandas)
#
#     def export(self, query, *args, **kwargs):
#         frames = []
#
#         for q in query:
#             frame = pandas.DataFrame(self.flatten(q))
#             frames.append(frame)
#
#         df = pandas.concat(frames)
#         df.index = range(len(query))
#         columns = df.columns
#         correct = []
#
#         for x in range(0, len(columns)):
#             if type(columns[x]) is tuple:
#                 correct.append(', '.join(columns[x]))
#             else:
#                 correct.append(columns[x])
#         df.columns = correct
#
#         return df
#
#     def flatten(self, record):
#         result = {}
#
#         # Query results are python dictionaries.
#         for k, v in record.iteritems():
#             # The function will create a DataFrame
#             # with separate columns for each
#             # key and subkey pair.
#             if type(v) is dict:
#                 for x, y in v.iteritems():
#                     result[(str(k), str(x))] = [y]
#             elif type(v) is list:
#                 if len(v) == 1:
#                     # Value is list with one dictionary.
#                     if type(v[0]) is dict:
#                         for item in v:
#                             if type(item) is dict:
#                                 for m, n in item.iteritems():
#                                     if n is not None:
#                                        result[(str(k), str(m))] = [
#                                            ''.join(n)]
#                     # Value is list with one non-dict value.
#                     else:
#                         result[(k)] = v
#                 else:
#                     # Value is list of  dictionaries.
#                     if type(v[0]) is dict:
#                         end = ''
#                         count = 0
#                         for item in v:
#                             sub_end = []
#                             for m, n in item.iteritems():
#                                 if type(n) is list:
#                                     n = ', '.join(n)
#                                 sub_end.append(str(m) + ': ' + str(n))
#                             end += ', '.join(sub_end) + '\r\n'
#                             count += 1
#                         result[(str(k), '*nested*')] = [end]
#                     # Value is list of length greater than 1.
#                     else:
#                         result[(k)] = [', '.join(str(elem) for elem in v)]
#             else:
#                 result[(k)] = [v]
#
#         return result


export = Exporter()
export.register(CSVExporter)
# export.register(PandasExporter)
