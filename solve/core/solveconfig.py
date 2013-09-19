"""
Solve Config Management
^^^^^^^^^^^^^^^^^^^^^^^

Manages the ~/.solve directory config files.

"""
import os
import json


class SolveConfig(object):
    base_path = os.path.expanduser('~/.solve')

    def __init__(self):
        if not os.path.isdir(self.base_path):
            os.makedirs(self.base_path)

    def get_path(self, name):
        return os.path.join(self.base_path, name)

    def load_json(self, name):
        config_file_path = self.get_path(name)
        if os.path.exists(config_file_path):
            fp = open(config_file_path, 'r')
            return json.load(fp)
        return None

    def save_json(self, name, data):
        fp = open(self.get_path(name), 'w')
        json.dump(data, fp, sort_keys=True, indent=4)
        fp.close()


solveconfig = SolveConfig()
