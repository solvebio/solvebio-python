# -*- coding: utf-8 -*-
"""
SolveBio Python Client
~~~~~~~~~~~~~~~~~~~~~~

This is the Python client & library for the SolveBio API.

Have questions or comments? email us at: support@solvebio.com
"""
from __future__ import absolute_import
from __future__ import print_function
__docformat__ = 'restructuredtext'

import os as _os
import logging as _logging
from .help import open_help as _open_help

# Capture warnings (specifically from urllib3)
try:
    _logging.captureWarnings(True)
except:
    # Python 2.6 doesn't support this
    pass

# Read/Write API key
api_key = _os.environ.get('SOLVEBIO_API_KEY', None)
# OAuth2 access tokens
access_token = _os.environ.get('SOLVEBIO_ACCESS_TOKEN', None)
api_host = _os.environ.get('SOLVEBIO_API_HOST', 'https://api.solvebio.com')


def help():
    _open_help('/docs')


def _init_logging():
    loglevel_base = _os.environ.get('SOLVEBIO_LOGLEVEL', 'WARN')
    loglevel_stream = _os.environ.get('SOLVEBIO_LOGLEVEL', 'WARN')
    logfile = _os.environ.get('SOLVEBIO_LOGFILE', '~/.solvebio/solvebio.log')
    loglevel_file = _os.environ.get('SOLVEBIO_LOGLEVEL', 'DEBUG')

    base_logger = _logging.getLogger("solvebio")
    base_logger.setLevel(loglevel_base)

    # clear handlers if any exist
    handlers = base_logger.handlers[:]
    for handler in handlers:
        base_logger.removeHandler(handler)
        handler.close()

    if loglevel_stream:
        stream_handler = _logging.StreamHandler()
        stream_handler.setLevel(loglevel_stream)
        stream_fmt = _logging.Formatter('[SolveBio] %(message)s')
        stream_handler.setFormatter(stream_fmt)
        base_logger.addHandler(stream_handler)

    if logfile:
        logfile_path = _os.path.expanduser(logfile)
        logdir = _os.path.dirname(logfile_path)

        if not _os.path.isdir(logdir):
            # Handle a race condition here when running
            # multiple services that import this package.
            try:
                _os.makedirs(logdir)
            except OSError as err:
                # Re-raise anything other than 'File exists'.
                if err[1] != 'File exists':
                    raise err

        file_handler = _logging.FileHandler(logfile_path)
        file_handler.setLevel(loglevel_file)
        file_fmt = _logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_fmt)
        base_logger.addHandler(file_handler)

    try:
        base_logger.addHandler(_logging.NullHandler())
    except:
        # supports Python < 2.7
        class NullHandler(_logging.Handler):
            def emit(self, record):
                pass

        base_logger.addHandler(NullHandler())


_init_logging()

from .version import VERSION  # noqa
from .errors import SolveError
from .query import Query, BatchQuery, Filter, GenomicFilter
from .annotate import Annotator, Expression
from .client import SolveClient
from .resource import (
    Application,
    Beacon,
    BeaconSet,
    Dataset,
    DatasetCommit,
    DatasetExport,
    DatasetField,
    DatasetImport,
    DatasetMigration,
    DatasetTemplate,
    DatasetRestoreTask,
    DatasetSnapshotTask,
    Group,
    Manifest,
    Object,
    User,
    Vault,
    VaultSyncTask,
    ObjectCopyTask,
    SavedQuery,
    Task
)


def login(**kwargs):
    """
    Sets up the auth credentials using the provided key/token,
    or checks the credentials file (if no token provided).

    Lookup order:
        1. access_token
        2. api_key
        3. local credentials

    No errors are raised if no key is found.
    """
    from .cli.auth import get_credentials
    global access_token, api_key, api_host

    # Clear any existing auth keys
    access_token, api_key = None, None
    # Update the host
    api_host = kwargs.get('api_host') or api_host

    if kwargs.get('access_token'):
        access_token = kwargs.get('access_token')
    elif kwargs.get('api_key'):
        api_key = kwargs.get('api_key')
    else:
        creds = get_credentials()
        # creds = (host, email, token_type, token)
        if creds:
            api_host = creds[0]
            if creds[2] == 'Bearer':
                access_token = creds[3]
            else:
                # By default, assume it is an API key.
                api_key = creds[3]

    # Always update the client host, version and agent
    from solvebio.client import client
    client.set_host()
    client.set_user_agent(name=kwargs.get('name'),
                          version=kwargs.get('version'))

    if not (api_key or access_token):
        return False
    else:
        # Update the client token
        client.set_token()
        return True


__all__ = [
    'Annotator',
    'Application',
    'Expression',
    'BatchQuery',
    'Beacon',
    'BeaconSet',
    'Dataset',
    'DatasetCommit',
    'DatasetField',
    'DatasetExport',
    'DatasetImport',
    'DatasetMigration',
    'DatasetTemplate',
    'DatasetRestoreTask',
    'DatasetSnapshotTask',
    'Filter',
    'GenomicFilter',
    'Group',
    'Manifest',
    'Object',
    'ObjectCopyTask',
    'Query',
    'SavedQuery',
    'SolveClient',
    'SolveError',
    'VaultSyncTask',
    'Task',
    'Vault',
    'User',
    'VERSION'
]
