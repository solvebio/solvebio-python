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


import logging
import os

# TODO: put these in SolveConfig
LOGLEVEL_STREAM = os.environ.get('SOLVE_LOGLEVEL_STREAM', 'WARNING')
LOGLEVEL_FILE = os.environ.get('SOLVE_LOGLEVEL_FILE', 'WARNING')


def _init_logging():
    base_logger = logging.getLogger("solvebio")
    base_logger.setLevel('DEBUG')

    #clear handlers if any exist
    handlers = base_logger.handlers[:]
    for handler in handlers:
        base_logger.removeHandler(handler)
        handler.close()

    if LOGLEVEL_STREAM:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(LOGLEVEL_STREAM)
        stream_fmt = logging.Formatter('[SolveBio] %(message)s')
        stream_handler.setFormatter(stream_fmt)
        base_logger.addHandler(stream_handler)

    if LOGLEVEL_FILE:
        logfile_path = os.path.expanduser('~/.solvebio/solvebio.log')
        if not os.path.isdir(os.path.dirname(logfile_path)):
            os.makedirs(os.path.dirname(logfile_path))

        file_handler = logging.FileHandler(logfile_path)
        file_handler.setLevel(LOGLEVEL_FILE)
        file_fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_fmt)
        base_logger.addHandler(file_handler)

    try:
        base_logger.addHandler(logging.NullHandler())
    except:
        # supports Python < 2.7
        class NullHandler(logging.Handler):
            def emit(self, record):
                pass

        base_logger.addHandler(NullHandler())

    return base_logger

solvelog = _init_logging()
