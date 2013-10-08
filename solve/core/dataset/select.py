# -*- coding: utf-8 -*-
#
# Copyright © 2013 Solve, Inc. <http://www.solvebio.com>. All rights reserved.
#
# email: contact@solvebio.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from .filters import Filter
from ..client import client
from ..solvelog import solvelog
from ..utils.printing import red, pretty_int
from ..utils.tabulate import tabulate


class Select(object):
    """
    Select API request wrapper.
    Generates JSON for the API call.
    """

    def __init__(self, namespace, *filters, **kwargs):
        self._namespace = namespace
        self._path = self._path_from_namespace(namespace)
        self._filters = []
        self.filter(*filters, **kwargs)

    def rewind(self):
        self._rows_received = None
        self._scroll_id = None
        self._row_sample = None
        self._row_cache = []

    def filter(self, *filters, **kwargs):
        """
        Returns this Select instance with the query args combined with
        existing set with AND.

        kwargs are simply passed to a new Filter object and combined to any
        other filters with AND.

        By default, everything is combined using AND. If you provide
        multiple filters in a single filter call, those are ANDed
        together. If you provide multiple filters in multiple filter
        calls, those are ANDed together.

        If you want something different, use the F class which supports
        ``&`` (and), ``|`` (or) and ``~`` (not) operators. Then call
        filter once with the resulting Filter instance.
        """
        self.rewind()
        for f in list(filters):
            if not isinstance(f, Filter):
                solvelog.warning('Filter non-keyword arguments must be Filter objects.')
            else:
                self._filters.append(f)

        if kwargs:
            self._filters += [Filter(**kwargs)]

        return self

    def _path_from_namespace(self, namespace):
        if namespace.startswith('solve.data.'):
            namespace = namespace[11:]
        return namespace.replace('.', '/')

    def __repr__(self):
        """
        Prints a summary of the Select object.
        """

        if self._rows_received is None:
            return u'<Select on %s (not executed)>' % self._namespace
        elif self._rows_received == 0:
            return u'<Select on %s (0 results)>' % self._namespace
        else:
            return u'\n%s\n\n... %s more results.' % (
                    tabulate(self._row_sample.items(), ['Columns', 'Sample']),
                    pretty_int(self._rows_total - 1))

    def __len__(self):
        """
        Executes select and returns the total number of results
        """
        if not self._scroll_id:
            self.execute()
        return self._rows_total

    def __getitem__(self, key):
        """
        Handle indexed lookups of cached rows.
        """
        try:
            if isinstance(key, slice):
                return [SelectResult(r) for r in self._row_cache[key]]
            else:
                return SelectResult(self._row_cache[key])
        except (KeyError, IndexError):
            print red('Slicing of Select objects is not fully supported. Please iterate instead.')

    def __iter__(self):
        """
        Execute a select and iterate through the result set.
        Once the cached result set is exhausted, repeat select.
        """
        # Always rewind on new iteration
        self.rewind()
        return self.execute()

    def next(self):
        """
        Allows the Select object to be an iterable.
        """
        if self._rows_received is None:
            # If next() is called prior to executing the select
            self.rewind()
            self.execute()

        if len(self._row_cache) == 0:
            # The select should always have been executed
            if self._rows_received < self._rows_total:
                # If result cache is empty, request more
                self.execute()
            else:
                # no more rows to fetch!
                raise StopIteration
        else:
            return SelectResult(self._row_cache.pop())

    def _build_query(self):
        qs = {}
        if self._filters:
            filters = self._process_filters(self._filters)
            if len(filters) > 1:
                qs['filters'] = {'and': filters}
            else:
                qs['filters'] = filters

        return qs

    def _process_filters(self, filters):
        """Takes a list of filters and returns JSON

        :arg filters: list of Filters, (key, val) tuples, or dicts

        :returns: list of JSON API filters

        """
        rv = []
        for f in filters:
            if isinstance(f, Filter):
                if f.filters:
                    rv.extend(self._process_filters(f.filters))
                    continue

            elif isinstance(f, dict):
                key = f.keys()[0]
                val = f[key]

                if isinstance(val, dict):
                    filter_filters = self._process_filters(val)
                    if len(filter_filters) == 1:
                        filter_filters = filter_filters[0]
                    rv.append({key: filter_filters})
                else:
                    rv.append({key: self._process_filters(val)})
            else:
                rv.extend((f,))
        return rv

    def execute(self):
        """
        Executes select and returns self (Select)

        Always sends a query, regardless of state.

        :returns: the resulting row objects

        """

        # If there's a scroll_id, continue scrolling
        if self._scroll_id:
            response = client.get_dataset_select(self._path,
                            {'scroll_id': self._scroll_id})
            self._rows_received += len(response['results'])
        else:
            # Otherwise, start a new scroll
            response = client.post_dataset_select(self._path, self._build_query())
            self._rows_total = response['total']
            self._rows_received = len(response['results'])

        self._scroll_id = response['scroll_id']
        self._row_cache = response['results'] + self._row_cache
        response['results'].reverse()  # setup for pop()ing

        # store a sample row
        if self._row_sample is None and self._rows_received:
            self._row_sample = SelectResult(self._row_cache[0])

        return self


class SelectResult(object):
    def __init__(self, obj):
        for k, v in obj.items():
            if k == 'metadata':
                self.metadata = SelectResult(v)
            else:
                setattr(self, k, v)

    def __getitem__(self, name):
        return getattr(self, name)

    def __repr__(self):
        return str(self.values())

    def keys(self):
        return [k for k, v in self.items()]

    def values(self):
        return [v for k, v in self.items()]

    def items(self):
        return [(k, v) for k, v in self.__dict__.items() if not k.startswith('_')]
