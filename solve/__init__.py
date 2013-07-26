"""
Copyright (c) 2013 `Solve, Inc. <http://www.solvebio.com>`_.  All rights reserved.
"""

# Load databases
try:
    db
except NameError:
    import db as _db
    db = _db.rootdb

# Load Root Helper
import help as _help
help = _help.BaseHelper("""Solve Shell.
Help TBD
""")

__version__ = '0.0.1'
__all__ = ['__version__', 'db', 'help']
