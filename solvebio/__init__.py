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
"""
SolveBio Python Client
~~~~~~~~~~~~~~~~~~~

This is the Python client & library for the SolveBio API.

Have questions or comments? email us at: contact@solvebio.com

"""


__author__ = 'Solve, Inc. <contact@solvebio.com>'
__version__ = '0.2.1'

from .core.dataset import directory as data


def help():
    # TODO: make fancy with colors!
    print """
The SolveBio Shell.

To list available datasets, type:

    solvebio.data.help()


To get some data, use the select() function, for example:

    solvebio.data.TCGA.somatic_mutations.select()


You may filter on any field in the datset. To see the fields for any dataset,
use the help() function, for example:

    solvebio.data.TCGA.somatic_mutations.help()


Enjoy using SolveBio!"""


__all__ = ['__version__', 'data', 'help']
