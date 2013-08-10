from importlib import import_module
from solve.help import BaseHelp


class BaseDatabase(object):
    """The base Database object which contains the heirarchy of
    namespaces and schemas."""

    def __init__(self, namespace, schema=None):
        self._metadata = {}
        self._namespace = namespace
        self._load_schema(schema)
        self.help = BaseHelp("Help for: %s" % self._namespace)

    def _load_schema(self, schema):
        if not schema:
            return

        for k, v in schema.items():
            if k.startswith('__'):
                self._metadata[k] = v
            else:
                sub_namespace = '.'.join([self._namespace, k])
                # Try to find namespace as a local module
                # if we find it, then import the Database class.
                # otherwise, use BaseDatabase
                try:
                    mod = import_module(sub_namespace)
                    custom_db = getattr(mod, 'Database')
                    self.__dict__[k] = custom_db(sub_namespace, v)
                except (AttributeError, ImportError):
                    self.__dict__[k] = BaseDatabase(sub_namespace, v)

    def select(self):
        raise NotImplementedError('select not implemented for %s' % self)

    def __repr__(self):
        return self.help.__repr__()

    def __str__(self):
        return self._namespace


class RootDatabase(BaseDatabase):
    def __init__(self, namespace='solve.db', schema=None):
        print "Loading databases..."
        super(RootDatabase, self).__init__(namespace, schema)
