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


from .solvelog import solvelog
from .client import client
from .utils.tabulate import tabulate
from .select import Select, Filter


class NamespaceDirectory(object):
    """
    The Directory is a singleton used to contain all Namespaces.
    """

    def __init__(self):
        self._name = 'solvebio.data'
        self._namespaces = None  # lazy loaded

    def __repr__(self):
        return '<NamespaceDirectory: %s>' % self._name

    def __str__(self):
        return self._name

    def __dir__(self):
        return [k['name'] for k in self._get_namespaces()]

    def __getattr__(self, name):
        self._get_namespaces()
        return object.__getattribute__(self, name)

    def help(self):
        _content = 'All Online Namespaces:\n\n'
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
            for ds in self._datasets:
                path = '%s.%s' % (ds['namespace'], ds['name'])
                self.__dict__[ds['name']] = Dataset(path, **ds)

        return self._datasets

    def help(self):
        _content = 'Datasets in %s:\n\n' % self._name
        _content += tabulate([('%s.%s' % (d['namespace'], d['name']), d['title'])
                              for d in self._get_datasets()],
                              ['Dataset', 'Title'])
        print _content


class Dataset(object):
    """
    Stores a Dataset and its fields
    """

    def __init__(self, path, **meta):
        assert len(path.split('.')) == 2, "Dataset name not valid. " \
                "Make sure it looks like: 'TCGA.mutations'"

        self._path = path
        self._dataset = None

        if not meta:
            # if no metadata is passed, we'll need to fetch it
            self._namespace, self._name = path.split('.')
            meta = self._get_dataset()

        for k, v in meta.items():
            # prefix each field with '_'
            self.__dict__['_' + k] = v

    def _get_dataset(self):
        if self._dataset is None:
            self._dataset = client.get_dataset(self._namespace, self._name)

        return self._dataset

    def select(self, *filters, **kwargs):
        """Create and return a new Select object with the set of Filters"""
        return Select(self._path).select(*filters, **kwargs)

    def range(self, chromosome, start, end, overlap=False):
        """Shortcut to do a range queries on supported Datasets"""
        range_filter = Filter(**{
                        '_coordinate_start__range': [int(start), int(end)],
                        '_coordinate_end__range': [int(start), int(end)]})
        chrom_filter = Filter(_chromosome=str(chromosome))
        if overlap:
            return Select(self._path).select(chrom_filter | range_filter)
        else:
            return Select(self._path).select(chrom_filter & range_filter)

    def help(self):
        fields = [(k['name'], k['data_type'], k['description']) for k
                    in sorted(self._get_dataset()['fields'], key=lambda k: k['name'])]
        print u'\nHelp for: %s\n%s\n%s\n\n%s\n\n' % (
                    self,
                    self._title,
                    self._description,
                    tabulate(fields, ['Field', 'Type', 'Description']))

    def __repr__(self):
        return '<Dataset: %s>' % self._path

    def __str__(self):
        return self._path


directory = NamespaceDirectory()
