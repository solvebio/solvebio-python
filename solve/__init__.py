"""
Solve
-----

Solve is the Python library the Solve API.

Questions, comments? contact@solvebio.com

Copyright (c) 2013 `Solve, Inc. <http://www.solvebio.com>`_.  All rights reserved.
"""

__author__ = 'David Caplan <dcaplan@solvebio.com>'
__version__ = '0.0.1'

try:
    data
except NameError:
    from .core.dataset import root as data


# Load Root Helper
import help as _help
help = _help.BaseHelp("""
The Solve Shell.
Help TBD
""")

__all__ = ['__version__', 'data', 'help']
