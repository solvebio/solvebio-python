"""
Solve Datasets
^^^^^^^^^^^^^^

By default Solve `select` arguments filters data with the AND boolean operator.

"""
from solve.core.solvelog import solvelog
from solve.help import BaseHelp
from .select import Select


class Dataset(object):
    """The Dataset object contains the heirarchy of
    namespaces and schemas."""

    def __init__(self, namespace, schema=None):
        self._metadata = {}
        self._namespace = namespace
        self._url = ''
        self.help = BaseHelp("Help for: %s" % self._namespace)
        if schema:
            self._load_schema(schema)
        else:
            # Get schema for namespace
            pass

    def _load_schema(self, schema):
        if not schema:
            return

        for k, v in schema.items():
            if k.startswith('__'):
                self._metadata[k] = v
            else:
                sub_namespace = '.'.join([self._namespace, k])
                self.__dict__[k] = Dataset(sub_namespace, v)

    def select(self, *filters, **kwargs):
        # Create and return a new Select object with the set of Filters
        return Select(self._namespace).filter(*filters, **kwargs)

    def __repr__(self):
        return self.help.__repr__()

    def __str__(self):
        return self._namespace


class RootDataset(Dataset):
    def __init__(self, schema, namespace='solve.data'):
        solvelog.debug('Initializing Root Dataset')
        super(RootDataset, self).__init__(namespace, schema)

# Schema format
ROOT_SCHEMA = {
    # The schema version
    '__version__': '0.0.1',
    # The user that it is for
    '__user_id__': '100',
    # The date it was downloaded (UTC)
    #   tz = pytz.timezone('US/Eastern')
    #   tz.normalize(tz.localize(datetime.datetime.now())).astimezone(pytz.utc)
    '__date__': '2013-07-30 22:44:15.918456+00:00',

    'TCGA': {
        '__name__': 'The Cancer Genome Atlas',
        'somatic_mutations': {
            '__name__': 'Somatic Mutations'
        }
    },
    'ENCODE': {
        '__name__': 'ENCODE',
        '__description__': 'The Encyclopedia of DNA Elements',
    },
    'KGP': {
        '__name__': '1000 Genomes',
        '__description__': 'The 1000 Genomes Project',
        'SNP': {
            '__name__': 'SNPs'
        }
    }
    # # User-specific datasets
    # 'davecap': {
    #     '__name__': 'Davecap\'s datasets on Solve',
    #     '__path__': '/davecap',
    #     'my-first-dataset': {
    #         # ...
    #     }
    # }
}
root = RootDataset(ROOT_SCHEMA)
