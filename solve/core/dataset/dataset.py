"""
Solve Datasets
^^^^^^^^^^^^^^

By default Solve `select` arguments filters data with the AND boolean operator.

"""
from solve.core.solvelog import solvelog
from solve.core.solveconfig import solveconfig
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


class RootNamespace(Namespace):
    """The RootNamespace is a singleton used to contain all Namespaces."""

    # The complete set of Namespaces is cached locally using solveconfig
    _solveconfig_cache = 'root_namespace.json'

    def __init__(self, name):
        self._name = name
        cached_namespaces = solveconfig.load_json(self._solveconfig_cache)
        if cached_namespaces:
            self._add_namespaces(cached_namespaces)
        else:
            self.refresh()
        self.help = BaseHelp("Help for %s" % name)

    def _flush_namespaces(self):
        """Clear namespaces from RootNamespace and local cache"""
        for k in self.__dict__.keys():
            if k not in ['help', '_name']:
                del self.__dict__[k]

        solveconfig.save_json(self._solveconfig_cache, [])

    def _add_namespaces(self, namespaces):
        solveconfig.save_json(self._solveconfig_cache, namespaces)

        for namespace in namespaces:
            self.__dict__[namespace['name']] = Namespace(**namespace)

    def refresh(self):
        """Load datasets from API and save in a local cache"""
        solvelog.info('Updating Datasets...')
        self._flush_namespaces()
        self._add_namespaces(client.get_namespaces())


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
        return Select(self._name).filter(*filters, **kwargs).execute()

    def __repr__(self):
        return self.help.__repr__()

    def __str__(self):
        return self._name


root = RootNamespace('solve.data')
