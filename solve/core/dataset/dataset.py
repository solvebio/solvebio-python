"""
Solve Datasets
^^^^^^^^^^^^^^

By default Solve `select` arguments filters data with the AND boolean operator.

"""
from solve.core.solvelog import solvelog
from solve.core.client import client
from solve.help import BaseHelp
from .select import Select

import logging
logger = logging.getLogger('solve')


class Namespace(object):
    """Namespaces are named-containers of Datasets"""
    _meta_fields = ['name', 'title', 'description', 'url']

    def __init__(self, **meta):
        self._name = meta.get('name')

        self._meta = {}
        for f in self._meta_fields:
            self._meta[f] = meta.get(f)

        self._add_datasets(meta.get('datasets'))

        self.help = BaseHelp("Help for: %s" % self._name)

    def _add_datasets(self, datasets):
        if not datasets:
            solvelog.warning('Namespace %s has no datasets!' % self._name)

        for dataset in datasets:
            self.__dict__[dataset['name']] = Dataset(**dataset)

    def __repr__(self):
        return self.help.__repr__()

    def __str__(self):
        return self._name


class Dataset(object):
    _meta_fields = ['name', 'full_name', 'title', 'description', 'url']

    def __init__(self, **meta):
        self._name = meta.get('full_name')

        self._meta = {}
        for f in self._meta_fields:
            self._meta[f] = meta.get(f)

        self.help = BaseHelp("Help for: %s" % self._name)

    def select(self, *filters, **kwargs):
        # Create and return a new Select object with the set of Filters
        return Select(self._name).filter(*filters, **kwargs)

    def __repr__(self):
        return self.help.__repr__()

    def __str__(self):
        return self._name


class RootNamespace(Namespace):
    def __init__(self, name, namespaces):
        self._name = name
        for namespace in namespaces:
            self.__dict__[namespace['name']] = Namespace(**namespace)
        self.help = BaseHelp("Help for solve.data")


solvelog.debug('Initializing Namespaces & Datasets...')
# TODO: Get schema from local cache
root = RootNamespace('solve.data', client.get_namespaces())
