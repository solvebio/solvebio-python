# -*- coding: utf-8 -*-
"""
SolveBio Python Interactive Client
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the Python interactive shell interface to the SolveBio API.

Have questions or comments? email us at: contact@solvebio.com

"""

from solvebio.cli.auth import login, opts_logout, opts_whoami

# Add some convenience functions for an interactive shell

import __main__
__main__.whoami = lambda: opts_whoami(None)  # noqa
__main__.logout = lambda: opts_logout(None)  # noqa
__main__.login = login
