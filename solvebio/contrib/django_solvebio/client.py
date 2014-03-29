import logging
logger = logging.getLogger('django_solvebio')

from solvebio import SolveError, Dataset
from models import DatasetAlias
import app_settings


class SolveBio(object):

    def is_enabled(self):
        return bool(app_settings.API_KEY)

    def get_dataset_id(self, alias):
        if alias is not None and alias in app_settings.DATASET_ALIASES:
            return app_settings.DATASET_ALIASES[alias]

        try:
            return DatasetAlias.objects.get(alias=alias).dataset_id
        except DatasetAlias.DoesNotExist:
            pass

        return None

    def query(self, alias, filters=[], **kwargs):
        """
        Wraps the SolveBio query API by aliasing datasets.
        Accepts a list of filters and returns a Query object.

        Unlike the Dataset.query() method in the solvebio Python client,
        this method is not chainable.

        Returns a list on success and None on failure.
        """
        if not self.is_enabled():
            logger.warning(
                'SolveBio is not enabled, aborting query to %s', alias)
            return None

        dataset_id = self.get_dataset_id(alias)

        if not dataset_id:
            logger.warning(
                'Could not find SolveBiodataset with alias "%s", ',
                'aborting query',
                alias)
            return None

        try:
            return list(Dataset(dataset_id).query(filters=filters, **kwargs))
        except SolveError as e:
            logger.warning('Error querying SolveBio dataset "%s": %s',
                           dataset_id, str(e))
            return None


client = SolveBio()
