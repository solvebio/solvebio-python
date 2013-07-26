"""
Copyright (c) 2013 `Solve, Inc. <http://www.solvebio.com>`_.  All rights reserved.
"""

# TODO: Get latest ResourceRegistry version from API
# TODO: Check the local cache
ROOT_SCHEMA = {
    '__version__': '0.0.1',

    'TCGA': {
        'BRCA': {
            'somatic_mutations': None
        }
    },
    'ENCODE': {
    },
    'ThousandGenomes': {
    }
}

from .base import RootDatabase
print "Loading databases..."
rootdb = RootDatabase('solve.db', ROOT_SCHEMA)
