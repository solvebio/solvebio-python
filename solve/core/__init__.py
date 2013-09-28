"""
Copyright (c) 2013 `Solve, Inc. <http://www.solvebio.com>`_.  All rights reserved.
"""
import os

DOMAIN = os.environ.get('SOLVE_DOMAIN', 'solvebio.com')
USE_SSL = (DOMAIN == 'solvebio.com')
API_HOST = 'api.%s' % DOMAIN
HELP_HOST = 'help.%s' % DOMAIN

