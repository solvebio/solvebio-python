#!/usr/bin/python
# -*- coding: utf-8 -*-
import solvebio

import argparse
import sys


class SolveArgumentParser(argparse.ArgumentParser):
    """Custom parser that prints help on error"""

    def error(self, message):
        self.print_help(sys.stderr)
        self.exit(2, '%s: error: %s\n' % (self.prog, message))


def shell(args):
    """Open the SolveBio shell (IPython wrapper)"""

    from IPython.config.loader import Config
    try:
        # see if we're already inside IPython
        get_ipython
    except NameError:
        cfg = Config()
        prompt_config = cfg.PromptManager
        prompt_config.in_template = '[SolveBio] In <\\#>: '
        prompt_config.in2_template = '   .\\D.: '
        prompt_config.out_template = 'Out<\\#>: '
        banner1 = 'SolveBio Python shell started.'
        exit_msg = 'Quitting SolveBio shell.'
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
    ipshell = InteractiveShellEmbed(
        config=cfg,
        banner1=banner1,
        exit_msg=exit_msg)
    ipshell()


# CLI argument parsers
base_parser = SolveArgumentParser(
    description='The SolveBio bioinformatics environment.')
base_parser.add_argument(
    '--version', action='version',
    version='solvebio %s' % solvebio.version.VERSION)
base_parser.add_argument(
    '--api-host', help='Override the default SolveBio API host')
base_parser.add_argument(
    '--api-key', help='Manually provide an API key')

subcommands = base_parser.add_subparsers(
    title='subcommands',
    description="""Subcommands of the SolveBio CLI""",
    dest='subcommand')

# shell parser
shell_parser = subcommands.add_parser(
    'shell', help='Open the SolveBio Python shell')
shell_parser.set_defaults(func=shell)


# auth parsers
from .auth import (login as auth_login,
                   logout as auth_logout,
                   whoami as auth_whoami)

login_parser = subcommands.add_parser(
    'login', help='Login and save credentials')
login_parser.set_defaults(func=auth_login)

logout_parser = subcommands.add_parser(
    'logout', help='Logout and delete saved credentials')
logout_parser.set_defaults(func=auth_logout)

whoami_parser = subcommands.add_parser(
    'whoami', help='Show your SolveBio email address')
whoami_parser.set_defaults(func=auth_whoami)


def main():
    if len(sys.argv) == 1:
        # if no subcommand is issued, default to shell
        args = base_parser.parse_args(['shell'])
    else:
        args = base_parser.parse_args()

    if args.api_host:
        solvebio.api_host = args.api_host
    if args.api_key:
        solvebio.api_key = args.api_key

    args.func(args)
