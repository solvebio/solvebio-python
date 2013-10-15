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


from solve.core.solvelog import solvelog
from solve.core.client import client
from solve.core.utils.tabulate import tabulate
from solve.core.utils.printing import red

from .select import Select

import os
import time
import json
import logging
logger = logging.getLogger('solve')


class Namespace(object):
    """Namespaces are named-containers of Datasets"""
    _meta_fields = ['name', 'title', 'description', 'url']

    def __init__(self, **meta):
        self._name = meta.get('name')
        self._meta = {}
        for f in self._meta_fields:
            self._meta[f] = meta.get(f)
        self._add_datasets(meta.get('datasets'))

    def _add_datasets(self, datasets):
        if not datasets:
            solvelog.warning('Namespace %s has no datasets!' % self._name)

        for dataset in datasets:
            self.__dict__[dataset['name']] = Dataset(**dataset)

    def __repr__(self):
        return '<Namespace: %s>' % self._name

    def __str__(self):
        return self._name

    def _help_content(self):
        _content = 'Datasets in %s:\n\n' % self._name
        datasets = sorted([k for k in self.__dict__.iterkeys() if not k.startswith('_')])
        _content += tabulate([(k, self.__dict__[k])
                              for k in datasets], ['Dataset', 'Title'])
        return _content

    def help(self):
        print self._help_content()


class RootNamespace(Namespace):
    """
    The RootNamespace is a singleton used to contain all Namespaces.
    Also caches to a file in the user's home directory.
    """

    # The complete set of Namespaces is cached locally
    _cache_path = os.path.expanduser('~/.solve/root_namespace.json')

    def __init__(self, name):
        self._name = name
        self._add_namespaces(self._load_from_cache(), cache=False)
        if self._cache_is_stale():
            print red("Your datasets are out of date, please run 'solve update' from your terminal, or 'solve.data.update()' from the Python shell to update them")

    def update(self):
        """Load datasets from API and save in a local cache"""
        cached_namespaces = self._load_from_cache()

        self._flush_namespaces()
        # get update from the client
        new_namespaces = client.get_namespaces()
        self._add_namespaces(new_namespaces, cache=True)

        # make dataset update report
        old_datasets = self._flatten_namespaces(cached_namespaces)
        new_datasets = {}
        for new_path, title in self._flatten_namespaces(new_namespaces).items():
            if new_path not in old_datasets:
                new_datasets[new_path] = title

        # return report of new/updated datasets
        return new_datasets

    def help(self):
        print self._help_content()

    def _help_content(self):
        _content = 'All available datasets:\n\n'
        datasets = self._flatten_namespaces(self._load_from_cache())
        # show table of all available datasets
        _content += tabulate([(k, datasets[k])
                    for k in sorted(datasets.iterkeys())], ['Dataset', 'Title'])
        return _content

    def _flush_namespaces(self):
        """Clear namespaces from RootNamespace and local cache"""
        for k in self.__dict__.keys():
            if k not in ['help', '_name']:
                del self.__dict__[k]

        self._save_to_cache([])

    def _add_namespaces(self, namespaces, cache=False):
        for namespace in namespaces:
            self.__dict__[namespace['name']] = Namespace(**namespace)
        if cache:
            self._save_to_cache(namespaces)

    def _load_from_cache(self):
        if os.path.exists(self._cache_path):
            return json.load(open(self._cache_path, 'r'))
        return []

    def _save_to_cache(self, data):
        if not os.path.isdir(os.path.dirname(self._cache_path)):
            os.makedirs(os.path.dirname(self._cache_path))

        fp = open(self._cache_path, 'w')
        json.dump(data, fp, sort_keys=True, indent=4)
        fp.close()

    def _cache_is_stale(self):
        if os.path.exists(self._cache_path):
            return time.time() > os.path.getmtime(self._cache_path) + (60 * 60 * 24 * 5)
        else:
            return False

    def _flatten_namespaces(self, namespaces):
        """
        For a list namespaces and datasets from the API,
        flatten to dotted-notation
        """
        datasets = {}
        for n in namespaces:
            for d in n['datasets']:
                datasets['.'.join([n['name'], d['name']])] = d['title']
        return datasets


class Dataset(object):
    _meta_fields = ['name', 'full_name', 'title', 'description', 'url', 'mapping']

    def __init__(self, **meta):
        self._name = meta.get('full_name')

        self._meta = {}
        for f in self._meta_fields:
            self._meta[f] = meta.get(f)

    def select(self, *filters, **kwargs):
        # Create and return a new Select object with the set of Filters
        return Select(self._name, *filters, **kwargs)

    def help(self):
        print self._help_content()

    def _help_content(self):
        # Hide hidden fields
        mapping = [(k, m['type']) for k, m
                    in self._meta['mapping'].items()
                    if not k.startswith('_')]
        return u'\nHelp for: %s\n%s\n%s\n\n%s\n\n' % (
                    self,
                    self._meta['title'],
                    self._meta['description'],
                    tabulate(mapping, ['Columns', 'Type']))

    def __repr__(self):
        return '<Dataset: %s>' % self._name

    def __str__(self):
        return self._name


root = RootNamespace('solve.data')
