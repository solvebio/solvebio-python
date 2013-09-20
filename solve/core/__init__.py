"""
Copyright (c) 2013 `Solve, Inc. <http://www.solvebio.com>`_.  All rights reserved.
"""
import os

SOLVE_DOMAIN = os.environ.get('SOLVE_HOST', 'solvebio.com')
API_HOST = 'api.%s' % SOLVE_DOMAIN
HELP_HOST = 'help.%s' % SOLVE_DOMAIN

