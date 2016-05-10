# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

from six.moves.urllib.parse import urlparse
from six.moves.urllib.parse import unquote

import os
import sys
import datetime
import time

try:
    from collections import OrderedDict
except ImportError:
    # Python 2.6 compatibility
    from ordereddict import OrderedDict

import pyprind

from .utils.humanize import naturalsize

try:
    import unicodecsv as csv
except ImportError:
    import csv

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class QueryExporters(object):
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
            raise Exception('Invalid exporter: {0}. Available exporters: {1}'
                            .format(exporter, ', '.join(self.registry.keys())))

        nrecords = len(query)
        if nrecords == 0:
            raise Exception('There are no results to export.')
        elif nrecords > self.EXPORT_WARN and not force:
            print('To export {0} records, use `force=True`.'
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

        title = 'Exporting query to: {0}'.format(filename)

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

        fieldnames = self.key_map.keys()
        try:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            # writer.writeheader() is new in 2.7
            # The following is used for 2.6 compat:
            # writer.writeheader()
            writer.writerow(dict(zip(fieldnames, fieldnames)))
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


exporters = QueryExporters()
exporters.register(CSVExporter)
exporters.register(XLSXExporter)


# Bulk Dataset Exports

class DatasetExportFile(object):
    """PyCurl-wrapper for downloading files from a bulk Dataset export.
    """
    progress_template = ('%(percent)6d%% %(downloaded)12s %(speed)15s '
                         '%(eta)18s ETA' + ' ' * 4)
    eta_limit = 60 * 60 * 24 * 30
    max_retries = 5

    def __init__(self, url, path=None, show_progress=True):
        self.url = url
        self.show_progress = show_progress
        self.start_time = None
        self.content_length = 0
        self.downloaded = 0

        self.path = os.path.abspath(os.path.expanduser(path))
        self.parsed_url = urlparse(url)
        self.file_name = unquote(os.path.basename(self.parsed_url.path))

        # Get output path from URL if a dir is provided.
        if os.path.isdir(self.path):
            self.path = os.path.join(self.path, self.file_name)

        self._last_time = 0.0
        self._rst_retries = 0

    @property
    def is_finished(self):
        if os.path.exists(self.path):
            return self.content_length == os.path.getsize(self.path)

    def download(self):
        # On some machines, pycurl fails to import. Make sure this error
        # only gets raised when export is used, rather than on startup.
        import pycurl

        curl = pycurl.Curl()

        while not self.is_finished:
            try:
                if os.path.exists(self.path):
                    print("Resuming download for {0}".format(self.path))
                    mode = 'ab'
                    self.downloaded = os.path.getsize(self.path)
                    curl.setopt(pycurl.RESUME_FROM, self.downloaded)
                else:
                    mode = 'wb'

                with open(self.path, mode) as f:
                    curl.setopt(curl.URL, self.url)
                    curl.setopt(curl.WRITEDATA, f)
                    curl.setopt(curl.NOPROGRESS, 0)
                    curl.setopt(pycurl.FOLLOWLOCATION, 1)
                    curl.setopt(curl.PROGRESSFUNCTION, self.progress)
                    curl.perform()
            except pycurl.error as e:
                # transfer closed with n bytes remaining to read
                if e.args[0] == pycurl.E_PARTIAL_FILE:
                    pass
                # HTTP server doesn't seem to support byte ranges.
                # Cannot resume.
                elif e.args[0] == pycurl.E_HTTP_RANGE_ERROR:
                    break
                # Recv failure: Connection reset by peer
                elif e.args[0] == pycurl.E_RECV_ERROR:
                    if self._rst_retries < self.max_retries:
                        pass
                else:
                    raise e
                self._rst_retries += 1

        sys.stderr.write('\n')
        sys.stderr.flush()

    def progress(self, download_t, download_d, upload_t, upload_d):
        self.content_length = self.downloaded + int(download_t)

        if not self.show_progress or int(download_t) == 0:
            return
        elif self.start_time is None:
            self.start_time = time.time()

        duration = time.time() - self.start_time + 1
        speed = download_d / duration
        speed_s = naturalsize(speed, binary=True)
        speed_s += '/s'

        if speed == 0.0:
            eta = self.eta_limit
        else:
            eta = int((download_t - download_d) / speed)

        if eta < self.eta_limit:
            eta_s = str(datetime.timedelta(seconds=eta))
        else:
            eta_s = 'n/a'

        downloaded = self.downloaded + download_d
        downloaded_s = naturalsize(downloaded, binary=True)

        percent = int(downloaded / self.content_length * 100)
        params = {
            'downloaded': downloaded_s,
            'percent': percent,
            'speed': speed_s,
            'eta': eta_s,
        }

        if sys.stderr.isatty():
            p = (self.progress_template + '\r') % params
        else:
            current_time = time.time()
            if self._last_time == 0.0:
                self._last_time = current_time
            else:
                interval = current_time - self._last_time
                if interval < 0.5:
                    return
                self._last_time = current_time
            p = (self.progress_template + '\n') % params

        sys.stderr.write(p)
        sys.stderr.flush()
