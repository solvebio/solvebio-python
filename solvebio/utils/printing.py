# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import locale
import logging

logger = logging.getLogger('solvebio')

try:
    reload(sys).setdefaultencoding(locale.getdefaultlocale()[1])
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

TTY_ROWS = 24
TTY_COLS = 80
TTY_COLORS = True

if sys.stdout.isatty():
    try:
        with open(os.devnull, 'w') as fnull:
            rows, cols = subprocess.check_output(
                ['stty', 'size'],
                stderr=fnull).split()
            TTY_ROWS = int(rows)
            TTY_COLS = int(cols)
    except:
        logger.warn('Cannot detect terminal column width')
else:
    TTY_COLORS = False


def pretty_int(num):
    return locale.format("%d", int(num), grouping=True)


# Basic color support

def green(text):
    if not TTY_COLORS:
        return text
    return '\033[32m' + text + '\033[39m'


def red(text):
    if not TTY_COLORS:
        return text
    return '\033[31m' + text + '\033[39m'


def yellow(text):
    if not TTY_COLORS:
        return text
    return '\033[33m' + text + '\033[39m'


def blue(text):
    if not TTY_COLORS:
        return text
    return '\033[34m' + text + '\033[39m'


def solve_bio():
    return blue('SolveBio')
