#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import sys
import copy
import argparse

import solvebio

from . import auth
from . import data
from .tutorial import print_tutorial
from .ipython import launch_ipython_shell
from ..utils.validators import validate_api_host_url
from ..utils.files import get_home_dir
from ..client import client


class TildeFixStoreAction(argparse._StoreAction):
    """A special "store" action for argparse that replaces
    any detected home directory with a tilde.
    (reverses bash's built-in ~ expansion).
    """
    def __call__(self, parser, namespace, values, option_string=None):
        home = get_home_dir()
        if values and values.startswith(home):
            values = values.replace(home, '~', 1)
        setattr(namespace, self.dest, values)


class SolveArgumentParser(argparse.ArgumentParser):
    """
    Main parser for the SolveBio command line client.
    """
    subcommands = {
        'login': {
            'func': auth.login,
            'help': 'Login and save credentials'
        },
        'logout': {
            'func': auth.logout,
            'help': 'Logout and delete saved credentials'
        },
        'whoami': {
            'func': auth.whoami,
            'help': 'Show your SolveBio email address'
        },
        'tutorial': {
            'func': print_tutorial,
            'help': 'Show the SolveBio Python Tutorial',
        },
        'shell': {
            'func': launch_ipython_shell,
            'help': 'Open the SolveBio Python shell'
        },
        'import': {
            'func': data.import_file,
            'help': 'Import a local file into a SolveBio dataset',
            'arguments': [
                {
                    'flags': '--create-dataset',
                    'action': 'store_true',
                    'help': 'Create the dataset if it doesn\'t exist',
                },
                {
                    'name': '--tag',
                    'help': 'A tag to be added. '
                    'Tags are case insensitive strings. Example tags: '
                    '--tag GRCh38 --tag Tissue --tag "Foundation Medicine"',
                    'action': 'append',
                },
                {
                    'flags': '--capacity',
                    'default': 'small',
                    'help': 'Specifies the capacity of the created dataset: '
                            'small (default, <100M records), '
                            'medium (<500M), large (>=500M)'
                },
                {
                    'flags': '--create-vault',
                    'action': 'store_true',
                    'help': 'Create the vault if it doesn\'t exist',
                },
                {
                    'flags': '--template-id',
                    'help': 'The template ID used when '
                            'creating a new dataset (via --create-dataset)',
                },
                {
                    'flags': '--template-file',
                    'help': 'A local template file to be used when '
                            'creating a new dataset (via --create-dataset)',
                },
                {
                    'flags': '--follow',
                    'action': 'store_true',
                    'default': False,
                    'help': 'Follow the import\'s progress until it completes'
                },
                {
                    'flags': '--commit-mode',
                    'default': 'append',
                    'help': 'Commit mode to use when importing data. '
                            'Options are "append" (default) or "overwrite".'
                },
                {
                    'name': 'full_path',
                    'help': 'The full path to the dataset in the format: '
                    '"domain:vault:/path/dataset". ',
                    'action': TildeFixStoreAction
                },
                {
                    'name': 'file',
                    'help': 'One or more local files to import',
                    'nargs': '+'
                },
            ]
        },
        'create-dataset': {
            'func': data.create_dataset,
            'help': 'Create a SolveBio dataset',
            'arguments': [
                {
                    'flags': '--create-vault',
                    'action': 'store_true',
                    'help': 'Create the vault if it doesn\'t exist',
                },
                {
                    'flags': '--template-id',
                    'help': 'The template ID used when '
                            'creating a new dataset (via --create-dataset)',
                },
                {
                    'flags': '--template-file',
                    'help': 'A local template file to be used when '
                            'creating a new dataset (via --create-dataset)',
                },
                {
                    'flags': '--capacity',
                    'default': 'small',
                    'help': 'Specifies the capacity of the dataset: '
                            'small (default, <100M records), '
                            'medium (<500M), large (>=500M)'
                },
                {
                    'name': '--tag',
                    'help': 'A tag to be added. '
                    'Tags are case insensitive strings. Example tags: '
                    '--tag GRCh38 --tag Tissue --tag "Foundation Medicine"',
                    'action': 'append',
                },
                # {
                #     'name': '--metadata',
                #     'help': 'Dataset metadata to be added. '
                #     'Metadata should be ....'
                # },
                {
                    'name': 'full_path',
                    'help': 'The full path to the dataset in the format: '
                    '"domain:vault:/path/dataset". '
                    'Defaults to your personal vault if no vault is provided. '
                    'Defaults to the vault root if no path is provided.',
                    'action': TildeFixStoreAction
                },
            ]
        },
        'upload': {
            'func': data.upload,
            'help': 'Upload a file or directory to a SolveBio Vault',
            'arguments': [
                {
                    'flags': '--full-path',
                    'help': 'The full path where the files and folders should '
                    'be created, defaults to the root of your personal vault',
                    'action': TildeFixStoreAction,
                    'default': '~/'
                },
                {
                    'flags': '--create-full-path',
                    'help': 'Creates --full-path location if it does '
                    'not exist. NOTE: This will not create new vaults.',
                    'action': 'store_true',
                },
                {
                    'flags': '--exclude',
                    'help': 'Paths to files or folder to be excluded from '
                    'upload. Unix shell-style wildcards are supported.',
                    'action': 'append'
                },
                {
                    'flags': '--dry-run',
                    'help': 'Dry run mode will not upload any files or '
                    'create any folders.',
                    'action': 'store_true'
                },
                {
                    'name': 'local_path',
                    'help': 'The path to the local file or directory '
                            'to upload',
                    'nargs': '+'
                }
            ]
        },
        'tag': {
            'func': data.tag,
            'help': 'Apply tags or remove tags on objects',
            'arguments': [
                {
                    'flags': 'full_path',
                    'help': 'The full path of the files, '
                    'folders or datasets to apply the tag updates. '
                    'Unix shell-style wildcards are supported. ',
                    'nargs': '+'
                },
                {
                    'name': '--tag',
                    'help': 'A tag to be added/removed. '
                    'Files, folders and datasets can be tagged. '
                    'Tags are case insensitive strings. Example tags: '
                    '--tag GRCh38 --tag Tissue --tag "Foundation Medicine"',
                    'action': 'append',
                    'required': True
                },
                {
                    'flags': '--remove',
                    'help': 'Will remove tags instead of adding them.',
                    'action': 'store_true'
                },
                {
                    'flags': '--exclude',
                    'help': 'Paths to files or folder to be excluded from '
                    'tagging. Unix shell-style wildcards are supported.',
                    'action': 'append'
                },
                {
                    'flags': '--tag-folders-only',
                    'help': 'Will only apply tags to folders (tags '
                    'all objects by default). ',
                    'action': 'store_true'
                },
                {
                    'flags': '--tag-files-only',
                    'help': 'Will only apply tags to files (tags '
                    'all objects by default). ',
                    'action': 'store_true'
                },
                {
                    'flags': '--tag-datasets-only',
                    'help': 'Will only apply tags to datasets (tags '
                    'all objects by default). ',
                    'action': 'store_true'
                },
                {
                    'flags': '--dry-run',
                    'help': 'Dry run mode will not save tags.',
                    'action': 'store_true'
                },
                {
                    'flags': '--no-input',
                    'help': 'Automatically accept changes (overrides '
                    'user prompt)',
                    'action': 'store_true'
                },
            ]
        },
    }

    def __init__(self, *args, **kwargs):
        super(SolveArgumentParser, self).__init__(*args, **kwargs)
        self._optionals.title = 'SolveBio Options'
        self.add_argument(
            '--version',
            action='version',
            version=solvebio.version.VERSION)
        self.add_argument(
            '--api-host',
            help='Override the default SolveBio API host',
            type=self.api_host_url)
        self.add_argument(
            '--api-key',
            help='Manually provide a SolveBio API key')
        self.add_argument(
            '--api-token',
            help='Manually provide a SolveBio OAuth API token')

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

        subcommands = copy.deepcopy(self.subcommands)
        for name, params in subcommands.items():
            p = subcmd.add_parser(name, help=params['help'])
            p.set_defaults(func=params['func'])
            for arg in params.get('arguments', []):
                name_or_flags = arg.pop('name', None) or arg.pop('flags', None)
                p.add_argument(name_or_flags, **arg)

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

    if not solvebio.api_key:
        # If nothing is set (via command line or environment)
        # look in local credentials
        try:
            from .credentials import get_credentials
            solvebio.api_key = get_credentials()
        except:
            pass

    # Update the client host and token
    client.set_host()
    client.set_token()

    return args.func(args)


if __name__ == '__main__':
    main()
