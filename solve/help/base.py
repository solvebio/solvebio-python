"""
Copyright (c) 2013 `Solve, Inc. <http://www.solvebio.com>`_.  All rights reserved.
"""


class BaseHelper(object):
    def __init__(self, longhelp):
        self._longhelp = longhelp

    def __repr__(self):
        return self._longhelp

    def __str__(self):
        return 'BaseHelper'
