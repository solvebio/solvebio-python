import os
import sys
import subprocess

from solve.core.solvelog import solvelog
from solve.core.solveconfig import solveconfig

solveconfig.set_default('TTY_ROWS', 24)
solveconfig.set_default('TTY_COLS', 80)
solveconfig.set_default('TTY_COLORS', True)

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
