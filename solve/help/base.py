"""
Copyright (c) 2013 `Solve, Inc. <http://www.solvebio.com>`_.  All rights reserved.
"""


class BaseHelp(object):
    def __init__(self, help):
        self._help = help

    def __repr__(self):
        return self._help

    def __str__(self):
        return 'BaseHelp'
