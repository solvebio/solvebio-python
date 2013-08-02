"""
Solve
-----

Solve is the Python library the Solve API.

Questions, comments? contact@solvebio.com

Copyright (c) 2013 `Solve, Inc. <http://www.solvebio.com>`_.  All rights reserved.
"""

__author__ = 'David Caplan <dcaplan@solvebio.com>'
__version__ = '0.0.1'

# Load databases
try:
    db
except NameError:
    import db as _db
    db = _db.root_db

# Load Root Helper
import help as _help
help = _help.BaseHelp("""
The Solve Shell.
Help TBD
""")

__all__ = ['__version__', 'db', 'help']
