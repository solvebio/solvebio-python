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

from .utils.tabulate import tabulate


class BaseHelp(object):
    def __init__(self, help):
        self._help = help

    def __repr__(self):
        return self._help

    def __str__(self):
        return 'BaseHelp'


class DatasetHelp(BaseHelp):
    def __init__(self, dataset):
        self._dataset = dataset
        self._help = 'Help for %s' % self._dataset

    def __repr__(self):
        mapping = [(k, m['type']) for k, m in self._dataset._meta['mapping'].items()]
        return u'\nHelp for: %s\n%s\n%s\n\n%s\n\n' % (
                    self._dataset,
                    self._dataset._meta['title'],
                    self._dataset._meta['description'],
                    tabulate(mapping, ['Columns', 'Type']))


solvehelp = BaseHelp("""
The Solve Shell.
""")
