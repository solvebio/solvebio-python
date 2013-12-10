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


import os
import sys
import subprocess
import locale

try:
    reload(sys).setdefaultencoding(locale.getdefaultlocale()[1])
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from solvebio.core.solvelog import solvelog
from solvebio.core.solveconfig import solveconfig

if sys.stdout.isatty():
    try:
        with open(os.devnull, 'w') as fnull:
            rows, cols = subprocess.check_output(['stty', 'size'],
                                            stderr=fnull).split()
            solveconfig.TTY_ROWS = int(rows)
            solveconfig.TTY_COLS = int(cols)
    except:
        solvelog.warn('Cannot detect terminal column width')
else:
    solveconfig.TTY_COLORS = False


def pretty_int(num):
    return locale.format("%d", int(num), grouping=True)


# Basic color support

def green(text):
    if not solveconfig.TTY_COLORS:
        return text
    return '\033[32m' + text + '\033[39m'


def red(text):
    if not solveconfig.TTY_COLORS:
        return text
    return '\033[31m' + text + '\033[39m'


def yellow(text):
    if not solveconfig.TTY_COLORS:
        return text
    return '\033[33m' + text + '\033[39m'


def blue(text):
    if not solveconfig.TTY_COLORS:
        return text
    return '\033[34m' + text + '\033[39m'


def solve_bio():
    return blue('SolveBio')
