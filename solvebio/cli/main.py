#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import sys
import argparse

import solvebio

from . import auth
from .tutorial import print_tutorial
from .ipython import launch_ipython_shell
from ..utils.validators import validate_api_host_url


class SolveArgumentParser(argparse.ArgumentParser):
    """Main parser for the SolveBio command line client"""
    HELP = {
        'login': 'Login and save credentials',
        'logout': 'Logout and delete saved credentials',
        'whoami': 'Show your SolveBio email address',
        'shell': 'Open the SolveBio Python shell',
        'tutorial': 'Show the SolveBio Python Tutorial',
        'version': solvebio.version.VERSION,
        'api_host': 'Override the default SolveBio API host',
        'api_key': 'Manually provide a SolveBio API key'
    }

    def __init__(self, *args, **kwargs):
        super(SolveArgumentParser, self).__init__(*args, **kwargs)
        self._optionals.title = 'SolveBio Options'
        self.add_argument('--version', action='version',
                          version=self.HELP['version'])
        self.add_argument('--api-host', help=self.HELP['api_host'],
                            type=self.api_host_url)
        self.add_argument('--api-key', help=self.HELP['api_key'])

    def _add_subcommands(self):
        """
            The _add_subcommands method must be separate from the __init__
            method, as infinite recursion will occur otherwise, due to the fact
            that the __init__ method itself will be called when instantiating
            a subparser, as we do below
        """
        subcmd_params = {
            'title': 'SolveBio Commands',
            'dest': 'subcommands'
        }
        subcmd = self.add_subparsers(
            **subcmd_params)  # pylint: disable=star-args
        login_parser = subcmd.add_parser('login', help=self.HELP['login'])
        login_parser.set_defaults(func=auth.login)
        logout_parser = subcmd.add_parser('logout', help=self.HELP['logout'])
        logout_parser.set_defaults(func=auth.logout)
        whoami_parser = subcmd.add_parser('whoami', help=self.HELP['whoami'])
        whoami_parser.set_defaults(func=auth.whoami)
        tutorial_parser = subcmd.add_parser(
            'tutorial', help=self.HELP['tutorial'])
        tutorial_parser.set_defaults(func=print_tutorial)
        shell_parser = subcmd.add_parser('shell', help=self.HELP['shell'])
        shell_parser.set_defaults(func=launch_ipython_shell)

    def parse_solvebio_args(self, args=None, namespace=None):
        """
            Try to parse the args first, and then add the subparsers. We want
            to do this so that we can check to see if there are any unknown
            args. We can assume that if, by this point, there are no unknown
            args, we can append shell to the unknown args as a default.
            However, to do this, we have to suppress stdout/stderr during the
            initial parsing, in case the user calls the help method (in which
            case we want to add the additional arguments and *then* call the
            help method. This is a hack to get around the fact that argparse
            doesn't allow default subcommands.
        """
        try:
            sys.stdout = sys.stderr = open(os.devnull, 'w')
            _, unknown_args = self.parse_known_args(args, namespace)
            if not unknown_args:
                args.insert(0, 'shell')
        except SystemExit:
            pass
        finally:
            sys.stdout.flush()
            sys.stderr.flush()
            sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__
        self._add_subcommands()
        return super(SolveArgumentParser, self).parse_args(args, namespace)

    def api_host_url(self, value):
        validate_api_host_url(value)
        return value


def main(argv=sys.argv[1:]):
    """ Main entry point for SolveBio CLI """
    parser = SolveArgumentParser()
    args = parser.parse_solvebio_args(argv)

    if args.api_host:
        solvebio.api_host = args.api_host
    if args.api_key:
        solvebio.api_key = args.api_key

    args.func(args)

if __name__ == '__main__':
    main()
