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
from solve.core.help import BaseHelp, DatasetHelp
from .select import Select

import os
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

        self.help = BaseHelp("Help for: %s" % self._name)

    def _add_datasets(self, datasets):
        if not datasets:
            solvelog.warning('Namespace %s has no datasets!' % self._name)

        for dataset in datasets:
            self.__dict__[dataset['name']] = Dataset(**dataset)

    def __repr__(self):
        return self.help.__repr__()

    def __str__(self):
        return self._name


class RootNamespace(Namespace):
    """
    The RootNamespace is a singleton used to contain all Namespaces.
    Also caches to a file in the user's home directory.
    """

    # The complete set of Namespaces is cached locally
    _cache_path = os.path.expanduser('~/.solve/root_namespace.json')

    def __init__(self, name):
        self._name = name

        if not self._load_from_cache():
            self.update()

        self.help = BaseHelp("Help for %s" % name)

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

    def update(self):
        """Load datasets from API and save in a local cache"""
        solvelog.info('Updating Datasets...')
        self._flush_namespaces()
        self._add_namespaces(client.get_namespaces(), cache=True)

    def _load_from_cache(self):
        if os.path.exists(self._cache_path):
            fp = open(self._cache_path, 'r')
            self._add_namespaces(json.load(fp))
            return True
        else:
            return False

    def _save_to_cache(self, data):
        if not os.path.isdir(os.path.dirname(self._cache_path)):
            os.makedirs(os.path.dirname(self._cache_path))

        fp = open(self._cache_path, 'w')
        json.dump(data, fp, sort_keys=True, indent=4)
        fp.close()

    def __getattr__(self, name):
        try:
            super(RootNamespace, self).__getattr__(name)
        except AttributeError:
            raise Exception('Could not find the namespace %s.' % name)


class Dataset(object):
    _meta_fields = ['name', 'full_name', 'title', 'description', 'url', 'mapping']

    def __init__(self, **meta):
        self._name = meta.get('full_name')

        self._meta = {}
        for f in self._meta_fields:
            self._meta[f] = meta.get(f)

        self.help = DatasetHelp(self)

    def select(self, *filters, **kwargs):
        # Create and return a new Select object with the set of Filters
        return Select(self._name, *filters, **kwargs)

    def __repr__(self):
        return self.help.__repr__()

    def __str__(self):
        return self._name


root = RootNamespace('solve.data')
