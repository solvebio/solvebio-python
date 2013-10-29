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

from .select import Select

import logging
logger = logging.getLogger('solve')


class NamespaceDirectory(object):
    """
    The Directory is a singleton used to contain all Namespaces.
    """

    def __init__(self):
        self._name = 'solve.data'
        self._namespaces = None  # lazy loaded

    def __repr__(self):
        return '<Namespace: %s>' % self._name

    def __str__(self):
        return self._name

    def __dir__(self):
        return [k['name'] for k in self._get_namespaces()]

    def __getattr__(self, name):
        self._get_namespaces()
        return object.__getattribute__(self, name)

    def help(self):
        _content = 'All Namespaces:\n\n'
        _content += tabulate([(ns['name'], ns['title'])
                             for ns in self._get_namespaces()],
                             ['Namespace', 'Title'])
        print _content

    def _get_namespaces(self):
        if self._namespaces is None:
            # load Namespaces from API store in instance cache
            self._namespaces = sorted(client.get_namespaces(),
                                      key=lambda k: k['name'])
            for namespace in self._namespaces:
                self.__dict__[namespace['name']] = Namespace(**namespace)

        return self._namespaces


class Namespace(object):
    """Namespaces are named-containers of Datasets"""

    def __init__(self, **meta):
        self._datasets = None  # lazy loaded
        for k, v in meta.items():
            self.__dict__['_' + k] = v

    def __repr__(self):
        return '<Namespace: %s>' % self._name

    def __str__(self):
        return self._name

    def __dir__(self):
        return [k['name'] for k in self._get_datasets()]

    def __getattr__(self, name):
        self._get_datasets()
        return object.__getattribute__(self, name)

    def _get_datasets(self):
        if self._datasets is None:
            self._datasets = sorted(client.get_namespace(self._name)['datasets'],
                                    key=lambda k: k['name'])
            for dataset in self._datasets:
                self.__dict__[dataset['name']] = Dataset(**dataset)

        return self._datasets

    def help(self):
        _content = 'Datasets in %s:\n\n' % self._name
        _content += tabulate([(d['full_name'], d['title'])
                              for d in self._get_datasets()],
                              ['Dataset', 'Title'])
        print _content


class Dataset(object):
    """
    Stores a Dataset and its fields
    """

    def __init__(self, **meta):
        self._mapping = None  # lazy loaded
        for k, v in meta.items():
            # prefix each field with '_'
            self.__dict__['_' + k] = v

    def _get_mapping(self):
        if self._mapping is None:
            self._mapping = client.get_dataset(self._namespace, self._name)['mapping']

        return self._mapping

    def select(self, *filters, **kwargs):
        # Create and return a new Select object with the set of Filters
        return Select(self._full_name).filter(*filters, **kwargs)

    def help(self):
        # Hide hidden fields
        mapping = [(k, self._get_mapping()[k]['type']) for k
                    in sorted(self._get_mapping().iterkeys())
                    if not k.startswith('_')]
        print u'\nHelp for: %s\n%s\n%s\n\n%s\n\n' % (
                    self,
                    self._title,
                    self._description,
                    tabulate(mapping, ['Columns', 'Type']))

    def __repr__(self):
        return '<Dataset: %s>' % self._full_name

    def __str__(self):
        return self._full_name


directory = NamespaceDirectory()
