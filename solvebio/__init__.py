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
from typing import Literal
from .help import open_help as _open_help

# Capture warnings (specifically from urllib3)
try:
    _logging.captureWarnings(True)
except:
    # Python 2.6 doesn't support this
    pass


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


"""
This is a cached value of client._host, and is kept in for backwards compatibility
Use this with caution, as you should prefer relying on get_api_host() instead
"""
api_host = None


def _set_cached_api_host(host):
    global api_host
    api_host = host


from .version import VERSION  # noqa
from .errors import SolveError
from .query import Query, BatchQuery, Filter, GenomicFilter
from .global_search import GlobalSearch
from .annotate import Annotator, Expression
from .client import client, SolveClient
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


def login(
    api_host: str = None,
    api_key: str = None,
    access_token: str = None,
    name: str = None,
    version: str = None,
    debug: bool = False,
):
    """
    Function to login to the QuartzBio/EDP API when using EDP in a python script.
    Note that another function is used when CLI command `quartzbio login` is used!
    EDP checks user credentials & host URL from multiple sources, in the following order:

    1) Parameters provided (e.g. the parameters of this function)
    2) Environment variables (if the above parameters weren't provided)
    3) quartzbio credentials file stored in the user's HOME directory
        (if parameters and environment variables weren't found)

    :param api_host: the QuartzBio EDP instance's URL to access.
    :param access_token: your user's access token, which you can generate at the EDP website
        (user menu > `Personal Access Tokens`)
    :param api_key: Your API key. You can use this instead of providing an access token
    :param name: name
    :param version: version

    Example:
        .. code-block:: python

            import quartzbio
            quartzbio.login(
                api_host="https://solvebio.api.az.aws.quartz.bio",
                api_key=YOUR_API_KEY
            )
    """
    token_type: Literal["Bearer", "Token"] = None
    token: str = None

    if access_token:
        token_type = "Bearer"
        token = access_token
    elif api_key:
        token_type = "Token"
        token = api_key

    if api_host or token or debug:
        client.set_credentials(
            api_host, token, token_type=token_type, raise_on_missing=not debug, debug=debug
        )

    client.set_user_agent(name=name, version=version)


def whoami():
    try:
        user = client.whoami()
    except Exception as e:
        print("{} (code: {})".format(e.message, e.status_code))
    else:
        return user


def get_api_host():
    global api_host
    api_host = client._host

    return client._host


get_api_host()


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
    'GlobalSearch',
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
