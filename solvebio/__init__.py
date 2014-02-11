# -*- coding: utf-8 -*-
"""
SolveBio Python Client
~~~~~~~~~~~~~~~~~~~

This is the Python client & library for the SolveBio API.

Have questions or comments? email us at: contact@solvebio.com

"""
import os as _os
import logging as _logging
from .help import open_help as _open_help

api_key = _os.environ.get('SOLVEBIO_API_KEY', None)
api_host = _os.environ.get('SOLVEBIO_API_HOST', 'https://api.solvebio.com')


def help():
    _open_help('/docs')


def _init_logging():
    loglevel_base = _os.environ.get('SOLVEBIO_LOGLEVEL', 'WARN')
    loglevel_stream = _os.environ.get('SOLVEBIO_LOGLEVEL_STREAM', 'WARN')
    logfile = _os.environ.get('SOLVEBIO_LOGFILE', '~/.solvebio/solvebio.log')
    loglevel_file = _os.environ.get('SOLVEBIO_LOGLEVEL_STREAM', 'DEBUG')

    base_logger = _logging.getLogger("solvebio")
    base_logger.setLevel(loglevel_base)

    #clear handlers if any exist
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
        if not _os.path.isdir(_os.path.dirname(logfile_path)):
            _os.makedirs(_os.path.dirname(logfile_path))

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

from . import version
from resource import User, Depository, DepositoryVersion, Dataset, DatasetField
from query import Filter

__all__ = ['Depository', 'DepositoryVersion', 'Dataset',
           'DatasetField', 'User', 'Filter']
