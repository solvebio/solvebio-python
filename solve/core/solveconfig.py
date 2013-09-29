"""
Solve Config Management
^^^^^^^^^^^^^^^^^^^^^^^

Lazy-loaded config management.

"""
import os


class SolveConfig(object):
    _environ = ['API_HOST', 'API_SSL', 'LOGLEVEL_STREAM', 'LOGLEVEL_FILE']
    _defaults = {}

    def __init__(self):
        """Set defaults from valid environment variables"""
        for name in self._environ:
            if ('SOLVE_' + name) in os.environ:
                self.set_default(name, os.environ.get(name))

    def set_default(self, key, value):
        self._defaults[key] = value

    def __setattr__(self, name, value):
        if name.upper() == name:
            # If it's a valid SolveConfig name
            self.__dict__[name] = value
        else:
            self.__dict__[name] = value

    def __getattr__(self, name):
        if name.upper() == name:
            if name in self.__dict__:
                return self.__dict__[name]
            elif name in self._defaults:
                # Set the value from the default
                self.__dict__[name] = self._defaults[name]
                return self._defaults[name]
            else:
                return None
        else:
            return self.__dict__[name]


config = SolveConfig()
