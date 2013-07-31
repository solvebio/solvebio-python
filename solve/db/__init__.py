"""
Copyright (c) 2013 `Solve, Inc. <http://www.solvebio.com>`_.  All rights reserved.
"""

# TODO: how to get the root schema from the API
#   Send OPTIONS request to API_HOST
#

# OPTIONS request to get:
#   * select filter keys (columns)
#   * select filter values (dimensions)
#   * versions?
# GET to query
# Sample data?
# Response formats?


# Schema format
ROOT_SCHEMA = {
    # The schema version
    '__version__': '0.0.1',
    # The user that it is for
    '__user_id__': '100',
    # The date it was downloaded (UTC)
    #   tz = pytz.timezone('US/Eastern')
    #   tz.normalize(tz.localize(datetime.datetime.now())).astimezone(pytz.utc)
    '__date__': '2013-07-30 22:44:15.918456+00:00',

    'TCGA': {
        '__path__': '/TCGA',

        'BRCA': {
            '__verbose_name__': 'Breast Cancer',
            '__path__': '/TCGA/BRCA',

            'somatic_mutations': {
                '__path__': '/TCGA/BRCA/somatic_muations',
            }
        }
    },
    'ENCODE': {
        '__name__': 'ENCODE',
        '__verbose_name__': 'The Encyclopedia of DNA Elements',
        '__path__': '/ENCODE'
        # ...
    },
    'TGP': {
        '__name__': '1000 Genomes',
        '__verbose_name__': 'The 1000 Genomes Project',
        '__path__': '/1000Genomes'
        # ...
    },
    # User-specific datasets
    'davecap': {
        '__name__': 'Davecap\'s datasets on Solve',
        '__path__': '/davecap',
        'my-first-dataset': {
            # ...
        }
    }
}


from .base import RootDatabase
root_db = None


def init_databases():
    global root_db
    root_db = RootDatabase(schema=ROOT_SCHEMA)

init_databases()
