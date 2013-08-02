#!/usr/bin/python
"""
Copyright (c) 2013 `Solve, Inc. <http://www.solvebio.com>`_.  All rights reserved.
"""
import os
import json


class SolveConfig(object):
    base_path = None

    def __init__(self):
        self.base_path = os.path.join('~', '.solve')

    def _setup_base_dir(self):
        if not os.path.isdir(self.base_path):
            os.makedirs(self.base_path)

    def get_config(self, name):
        config_file_path = os.path.join(self.base_path, name)
        if os.path.exists(config_file_path):
            fp = open(config_file_path, 'r')
            return json.load(fp)
        return None

    def save_config(self, name, config):
        self._setup_base_dir()
        config_file_path = os.path.join(self.base_path, name)
        fp = open(config_file_path, 'w')
        json.dump(config, fp, sort_keys=True, indent=4)
        fp.close()


def get_local_credentials():
    return SolveConfig().get_config('credentials')


def signup():
    print "Signup to Solve..."


def login():
    print "Login with Solve..."


def logout():
    print "Logging out from Solve..."
