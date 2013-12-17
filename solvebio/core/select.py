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


import copy

from .client import client
from .solvelog import solvelog
from .utils.printing import pretty_int
from .utils.tabulate import tabulate


class Filter(object):
    """
    Filter objects.

    Makes it easier to create filters cumulatively using ``&`` (and),
    ``|`` (or) and ``~`` (not) operations.

    For example::

        f = F()
        f &= F(price='Free')
        f |= F(style='Mexican')

    creates a filter "price = 'Free' or style = 'Mexican'".

    Each set of kwargs in a `Filter` are ANDed together:

        * `<field>=''` uses a term filter (exact term)
        * `<field>__in=[]` uses a terms filter (match any)

    String terms are not analyzed and are always assumed to be exact matches.

    Numeric columns can be selected by range using:

        * `<field>__gt`: greater than
        * `<field>__gte`: greater than or equal to
        * `<field>__lt`: less than
        * `<field>__lte`: less than or equal to

    Field action examples:

        TCGA.somatic_mutations.select(gene__in=['BRCA', 'GATA3'],
                                      chr='3',
                                      start__gt=10000,
                                      end__lte=20000)
    """
    def __init__(self, **filters):
        """Creates a Filter"""
        filters = filters.items()
        if len(filters) > 1:
            self.filters = [{'and': filters}]
        else:
            self.filters = filters

    def __repr__(self):
        return '<Filter {0}>'.format(self.filters)

    def _combine(self, other, conn='and'):
        """
        OR and AND will create a new Filter, with the filters from both Filter
        objects combined with the connector `conn`.
        """
        f = Filter()

        self_filters = copy.deepcopy(self.filters)
        other_filters = copy.deepcopy(other.filters)

        if not self.filters:
            f.filters = other_filters
        elif not other.filters:
            f.filters = self_filters
        elif conn in self.filters[0]:
            f.filters = self_filters
            f.filters[0][conn].extend(other_filters)
        elif conn in other.filters[0]:
            f.filters = other_filters
            f.filters[0][conn].extend(self_filters)
        else:
            f.filters = [{conn: self_filters + other_filters}]

        return f

    def __or__(self, other):
        return self._combine(other, 'or')

    def __and__(self, other):
        return self._combine(other, 'and')

    def __invert__(self):
        f = Filter()
        self_filters = copy.deepcopy(self.filters)
        if len(self_filters) == 0:
            f.filters = []
        elif (len(self_filters) == 1
              and isinstance(self_filters[0], dict)
              and self_filters[0].get('not', {})):
            f.filters = self_filters[0]['not']
        else:
            f.filters = [{'not': self_filters}]
        return f


class Result(object):
    """
    Container for Select result key/value documents
    """
    def __init__(self, obj):
        for k, v in obj.items():
            if k == 'metadata':
                self.metadata = Result(v)
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
        # alphabetically sorted keys, excluding hidden keys (_*)
        return [(k, v) for k, v in sorted(self.__dict__.items(), key=lambda k: k[0])
                if not k.startswith('_')]


class Select(object):
    """
    A Select API request wrapper that generates a request from Filter objects,
    and can iterate through streaming result sets.
    """

    def __init__(self, dataset, result_class=Result):
        self._dataset = dataset  # a Dataset object
        self._result_class = result_class
        self._filters = []
        self._scroll_id = None
        self._results_received = None
        self._results_total = None
        self._results_cache = None
        self._cursor = None
        self._start = None
        self._stop = None

    def _clone(self, filters=None):
        new = self.__class__(self._dataset, self._result_class)
        new._filters = self._filters
        if filters is not None:
            new._filters += filters
        #new.__dict__.update(kwargs)
        return new

    def select(self, *filters, **kwargs):
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
        return self._clone(filters=list(filters) + [Filter(**kwargs)])

    def _build_query(self):
        q = {}
        if self._filters:
            filters = self._process_filters(self._filters)
            if len(filters) > 1:
                q['filters'] = [{'and': filters}]
            else:
                q['filters'] = filters

        return q

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

    def __len__(self):
        """
        Executes select and returns the total number of results
        """
        self._fetch_results()

        if self._start is not None:
            start = self._start
        else:
            start = 0
        if self._stop is not None and self._stop <= self._results_total:
            stop = self._stop
        else:
            stop = self._results_total

        return stop - start

    def __nonzero__(self):
        self._fetch_results()
        return bool(self._results_total)

    def __repr__(self):
        self._fetch_results()

        if self._results_total == 0:
            return u'Select on %s returned 0 results' % self._dataset

        return u'\n%s\n\n... %s more results.' % (
                tabulate(self[0].items(), ['Columns', 'Sample']),
                pretty_int(self._results_total - 1))

    def __getitem__(self, key):
        """
        Retrieve an item or slice from the set of results
        """
        if not isinstance(key, (slice, int, long)):
            raise TypeError

        assert ((not isinstance(key, slice) and (key >= 0))
                or (isinstance(key, slice) and (key.start is None or key.start >= 0)
                    and (key.stop is None or key.stop >= 0))), \
                "Negative indexing is not supported."

        if self._results_cache:
            # see if the result is cached already
            lower = self._results_received - len(self._results_cache)
            upper = self._results_received
            if isinstance(key, slice):
                if key.start is not None and key.start >= lower \
                    and key.stop is not None and key.stop <= upper:
                    return self._results_cache[key]
            elif key >= lower and key <= upper:
                return self._results_cache[key]

        if isinstance(key, slice):
            new = self._clone()
            if key.start is not None:
                new._start = int(key.start)
            if key.stop is not None:
                new._stop = int(key.stop)
            return list(new)[::key.step] if key.step else new

        # not a slice, just an index
        new = self._clone()
        new._start = key
        new._stop = key + 1
        return list(new)[0]

    def __iter__(self):
        """
        Execute a select and iterate through the result set.
        Once the cached result set is exhausted, repeat select.
        """
        # restart a fresh scroll
        self._start_scroll()

        # fast-forward the cursor if _start is requested
        if self._start:  # not None and > 0
            self._cursor = self._start
            while self._results_received < self._cursor:
                self._scroll()

            # slice the results_cache to put _start at 0 in the cache
            self._results_cache = \
                self._results_cache[self._cursor - self._results_received:]

        return self

    def next(self):
        """
        Allows the Select object to be an iterable.
        Iterates through the internal cache using a cursor.
        """
        # if next() is called on its own, make sure we have some results
        self._fetch_results()

        # If the cursor has reached the end
        if (self._stop is not None and self._cursor >= self._stop) \
            or self._cursor >= self._results_total:
            raise StopIteration

        cache_index = self._cursor - self._results_received
        if cache_index == 0:
            # If result cache is empty, request more
            self._scroll()
            cache_index = self._cursor - self._results_received

        self._cursor += 1
        return self._results_cache[cache_index]

    def _fetch_results(self):
        """
        Starts the scroll process and scrolls if in empty state
        """
        if self._scroll_id is None:
            self._start_scroll()

        if self._results_cache is None:
            if self._results_total == 0:
                self._results_cache = []
            else:
                self._scroll()

    def _start_scroll(self):
        response = client.post_dataset_select(self._dataset._namespace,
                    self._dataset._name, self._build_query())

        self._cursor = 0
        self._results_cache = None
        self._results_total = response['total']
        self._scroll_id = response['scroll_id']
        # should be 0 results received
        self._results_received = len(response['results'])
        if self._results_received:
            solvelog.warning('%d results from initial scroll ID fetch'
                                % len(self._results_cache))

        if self._start is not None and self._start >= self._results_total:
            raise IndexError('Index out of range, only %d total results(s)'
                                % self._results_total)

    def _scroll(self):
        response = client.get_dataset_select(self._dataset._namespace,
                    self._dataset._name, self._scroll_id)

        # TODO: handle scroll_id failure
        self._scroll_id = response['scroll_id']
        self._results_received += len(response['results'])
        # always overwrite the cache
        self._results_cache = [self._result_class(r) for r in response['results']]
