from __future__ import absolute_import
import os
from pydoc import pager

TUTORIAL = os.path.abspath(os.path.dirname(__file__)) + '/tutorial.md'


def print_tutorial(args):
    pager(open(TUTORIAL, 'rb').read())
