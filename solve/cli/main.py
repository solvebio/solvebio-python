#!/usr/bin/python
"""
The SolveBio command-line interface (CLI)

Copyright (c) 2013 `Solve, Inc. <http://www.solvebio.com>`_.  All rights reserved.
"""

import argparse

import solve

# CLI argument parsers
base_parser = argparse.ArgumentParser(description='The Solve bioinformatics environment.')
base_parser.add_argument('--version', action='version', version='solve %s' % (solve.__version__))

subcommands = base_parser.add_subparsers(title='subcommands',
    description="""Subcommands of the Solve CLI""",
    dest='_subcommand')

setup_parser = subcommands.add_parser('setup', help='Setup the Solve environment')
shell_parser = subcommands.add_parser('shell', help='Open the Solve shell (IPython)')


def main(args=None):
    parsed_args = base_parser.parse_args()
    subcommand_name = getattr(parsed_args, '_subcommand', '')

    subcommand_mapping = {
        'setup': setup,
        'shell': shell
    }

    kwargs = dict([(k, v) for k, v in parsed_args._get_kwargs() if not k.startswith('_')])
    return subcommand_mapping[subcommand_name](**kwargs)


def setup():
    print "Setting up Solve!"


def shell():
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

    import solve
    ipshell()
