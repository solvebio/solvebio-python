#!/usr/bin/python
"""
The SolveBio command-line interface (CLI)

Copyright (c) 2013 `Solve, Inc. <http://www.solvebio.com>`_.  All rights reserved.
"""

import argparse
import sys

from . import auth
import solve

# CLI argument parsers
base_parser = argparse.ArgumentParser(description='The Solve bioinformatics environment.')
base_parser.add_argument('--version', action='version', version='solve %s' % (solve.__version__))

subcommands = base_parser.add_subparsers(title='subcommands',
    description="""Subcommands of the Solve CLI""",
    dest='_subcommand')

shell_parser = subcommands.add_parser('shell', help='Open the Solve shell')
auth_parser = subcommands.add_parser('auth', help='Manage Solve authentication credentials')
auth_parser.add_argument('-login', action='store_true', default=False, help='Login and save credentials')
auth_parser.add_argument('-logout', action='store_true', default=False, help='Logout and delete saved credentials')
auth_parser.add_argument('-whoami', action='store_true', default=False, help='Show your Solve email address')


def main(args=None):
    if len(sys.argv) == 1:
        # If there are no args at all, default to the shell
        parsed_args = base_parser.parse_args(['shell'])
    else:
        parsed_args = base_parser.parse_args()

    subcommand_name = getattr(parsed_args, '_subcommand', '')
    subcommand_mapping = {
        'auth': auth_subcommand,
        'shell': shell_subcommand
    }

    kwargs = dict([(k, v) for k, v in parsed_args._get_kwargs() if not k.startswith('_')])
    return subcommand_mapping[subcommand_name](**kwargs)


def shell_subcommand(**kwargs):
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
    from IPython.frontend.terminal.embed import InteractiveShellEmbed

    # Now create an instance of the embeddable shell. The first argument is a
    # string with options exactly as you would type them if you were starting
    # IPython at the system command line. Any parameters you want to define for
    # configuration can thus be specified here.
    ipshell = InteractiveShellEmbed(config=cfg,
               banner1=banner1,
               exit_msg=exit_msg)
    ipshell()


def auth_subcommand(**kwargs):
    for cmd, run in kwargs.items():
        if run:
            try:
                getattr(auth, cmd)()
                sys.exit(0)
            except KeyboardInterrupt:
                sys.stderr.write('\nSetup interrupted. Please run "solve auth -%s" to restart.\n' % cmd)
                sys.exit(1)

    # No valid commands
    return auth_parser.print_help()
