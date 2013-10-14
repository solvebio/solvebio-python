#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright © 2013 Solve, Inc. <http://www.solvebio.com>. All rights reserved.
#
# email: contact@solvebio.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import solve

import argparse
import sys


class SolveArgumentParser(argparse.ArgumentParser):
    """Custom parser that prints help on error"""

    def error(self, message):
        self.print_help(sys.stderr)
        self.exit(2, '%s: error: %s\n' % (self.prog, message))


def shell(args):
    """Open the Solve shell (IPython wrapper)"""

    from IPython.config.loader import Config
    try:
        # see if we're already inside IPython
        get_ipython
    except NameError:
        cfg = Config()
        prompt_config = cfg.PromptManager
        prompt_config.in_template = '[Solve] In <\\#>: '
        prompt_config.in2_template = '   .\\D.: '
        prompt_config.out_template = 'Out<\\#>: '
        banner1 = 'Solve shell started.'
        exit_msg = 'Quitting Solve shell.'
    else:
        print("Running nested copies of IPython.")
        cfg = Config()
        banner1 = exit_msg = ''

    # First import the embeddable shell class
    try:
        from IPython.terminal.embed import InteractiveShellEmbed
    except ImportError:
        from IPython.frontend.terminal.embed import InteractiveShellEmbed

    # Now create an instance of the embeddable shell. The first argument is a
    # string with options exactly as you would type them if you were starting
    # IPython at the system command line. Any parameters you want to define for
    # configuration can thus be specified here.
    ipshell = InteractiveShellEmbed(config=cfg,
               banner1=banner1,
               exit_msg=exit_msg)
    ipshell()


# CLI argument parsers
base_parser = SolveArgumentParser(description='The Solve bioinformatics environment.')
base_parser.add_argument('--version', action='version', version='solve %s' % solve.__version__)
base_parser.add_argument('--api-host', help='Override the default Solve API host')

subcommands = base_parser.add_subparsers(title='subcommands',
    description="""Subcommands of the Solve CLI""",
    dest='subcommand')

# shell parser
shell_parser = subcommands.add_parser('shell', help='Open the Solve shell')
shell_parser.set_defaults(func=shell)


# auth parsers
from .auth import (login as auth_login,
                   logout as auth_logout,
                   whoami as auth_whoami)

login_parser = subcommands.add_parser('login', help='Login and save credentials')
login_parser.set_defaults(func=auth_login)

logout_parser = subcommands.add_parser('logout', help='Logout and delete saved credentials')
logout_parser.set_defaults(func=auth_logout)

whoami_parser = subcommands.add_parser('whoami', help='Show your Solve email address')
whoami_parser.set_defaults(func=auth_whoami)


# dataset parsers
def dataset_update(args=None):
    print 'Updating datasets...'
    report = solve.data.update()
    if report:
        print '\nNew datasets available!\n'
        for path, title in report.items():
            print '%s: %s' % (path, title)
        print ''

    # check for new version on pypi
    try:
        import requests
        r = requests.get('http://pypi.python.org/pypi/%s/json' % 'solve')
        new_version = r.json()['info']['version']
        if new_version != solve.__version__:
            print "A new version of solve (%s) is available! Run 'pip install solve --upgrade' to get it." % new_version
    except:
        pass

dataset_update_parser = subcommands.add_parser('update', help='Update the dataset cache')
dataset_update_parser.set_defaults(func=dataset_update)


def main(args=None):
    if len(sys.argv) == 1:
        # If there are no args at all, default to the shell
        args = base_parser.parse_args(['shell'])
    else:
        args = base_parser.parse_args()

    if args.api_host:
        from solve.core.solveconfig import solveconfig

        if args.api_host.startswith('http://'):
            solveconfig.API_SSL, solveconfig.API_HOST = False, args.api_host.replace('http://', '')
        elif args.api_host.startswith('https://'):
            solveconfig.API_SSL, solveconfig.API_HOST = True, args.api_host.replace('https://', '')
        else:
            solveconfig.API_HOST = args.api_host

    args.func(args)
