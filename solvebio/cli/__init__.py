# -*- coding: utf-8 -*-
"""
SolveBio Python Interactive Client
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the Python interactive shell interface to the SolveBio API.

Have questions or comments? email us at: contact@solvebio.com

"""

from solvebio.cli.auth import login, login_if_needed, opts_logout, opts_whoami

import sys
if len(sys.argv) <= 1:
    login_if_needed()

# Add some convenience functions for an interactive shell

import __main__
__main__.whoami = lambda: opts_whoami(None)  # noqa
__main__.logout = lambda: opts_logout(None)  # noqa
__main__.login = login
