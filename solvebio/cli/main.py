#!/usr/bin/env python
# -*- coding: utf-8 -*-
#pylint: disable=superfluous-parens
""" Main file for SolveBio CLI """

import os
import sys
import argparse

import solvebio

from . import auth

class SolveArgumentParser(argparse.ArgumentParser):
    """Main parser for the SolveBio command line client"""
    HELP = {
        'login' : 'Login and save credentials',
        'logout' : 'Logout and delete saved credentials',
        'whoami' : 'Show your SolveBio email address',
        'shell' : 'Open the SolveBio Python shell',
        'version' : '%(prog)s {}'.format(solvebio.version.VERSION),
        'api_host' : 'Override the default SolveBio API host',
        'api_key' : 'Manually provide a SolveBio API key'
    }

    def __init__(self, *args, **kwargs):
        super(SolveArgumentParser, self).__init__(*args, **kwargs)
        self._optionals.title = 'SolveBio Options'
        self.add_argument('--version', action='version',
                          version=self.HELP['version'])
        self.add_argument('--api-host', help=self.HELP['api_host'])
        self.add_argument('--api-key', help=self.HELP['api_key'])

    def _add_subcommands(self):
        """
            The _add_subcommands method must be separate from the __init__
            method, as infinite recursion will occur otherwise, due to the fact
            that the __init__ method itself will be called when instantiating
            a subparser, as we do below
        """
        subcmd_params = {
            'title' : 'SolveBio Commands',
            'dest' : 'subcommands'
        }
        subcmd = self.add_subparsers(**subcmd_params) #pylint: disable=star-args
        login_parser = subcmd.add_parser('login', help=self.HELP['login'])
        login_parser.set_defaults(func=auth.login)
        logout_parser = subcmd.add_parser('logout', help=self.HELP['logout'])
        logout_parser.set_defaults(func=auth.logout)
        whoami_parser = subcmd.add_parser('whoami', help=self.HELP['whoami'])
        whoami_parser.set_defaults(func=auth.whoami)
        shell_parser = subcmd.add_parser('shell', help=self.HELP['shell'])
        shell_parser.set_defaults(func=launch_ipython_shell)

    def parse_args(self, args=None, namespace=None):
        """
            Try to parse the args first, and then add the subparsers. We want
            to do this so that we can check to see if there are any unknown
            args. We can assume that if, by this point, there are no unknown
            args, we can append shell to the unknown args as a default. However,
            to do this, we have to suppress stdout/stderr while doing the
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

def launch_ipython_shell(args): #pylint: disable=unused-argument
    """Open the SolveBio shell (IPython wrapper)"""
    try:
        from IPython.config.loader import Config
    except ImportError:
        print("The SolveBio Python shell requires IPython.\n"
              "To install, type: 'pip install ipython'")
        return

    try:
        # see if we're already inside IPython
        get_ipython #pylint: disable=undefined-variable
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
        #pylint: disable=import-error,no-name-in-module
        from IPython.frontend.terminal.embed import InteractiveShellEmbed

    # Now create an instance of the embeddable shell. The first argument is a
    # string with options exactly as you would type them if you were starting
    # IPython at the system command line. Any parameters you want to define for
    # configuration can thus be specified here.
    InteractiveShellEmbed(config=cfg, banner1=banner1, exit_msg=exit_msg)()


def main(argv=sys.argv[1:]):
    """ Main entry point for SolveBio CLI """
    parser = SolveArgumentParser()
    args = parser.parse_args(argv)

    if args.api_host:
        solvebio.api_host = args.api_host
    if args.api_key:
        solvebio.api_key = args.api_key

    args.func(args)

if __name__ == '__main__':
    main()
