from django.db import models
import solvebio
import app_settings


class DatasetManager(models.Manager):
    def get(self, *args, **kwargs):
        alias = kwargs.get('alias', None)
        if alias is not None and alias in app_settings.DATASETS:
            # return a Dataset Model object
            return Dataset(alias=alias,
                           dataset_id=app_settings.DATASETS[alias])

        return super(DatasetManager, self).get(*args, **kwargs)


class Dataset(models.Model):
    """
    Base aliased-dataset model. You can use your own by subclassing this
    model and then specifying it in the SOLVEBIO_DATASET_MODEL setting.

    For example:

        SOLVEBIO_DATASET_MODEL = 'APP_NAME.MODEL_NAME'

    """
    alias = models.CharField(
        unique=True, db_index=True, max_length=100,
        help_text=("A local alias used to reference a versioned dataset"))
    dataset_id = models.CharField(
        max_length=100,
        help_text=("Can be an integer ID or a full name "
                   "(i.e. ClinVar/0.0.2/ClinVar)"))

    objects = DatasetManager()

    def query(self, filters=[], fail_silently=False):
        try:
            return solvebio.Dataset(self.dataset_id).query(filters=filters)
        except solvebio.SolveAPIError:
            if fail_silently:
                return None
            raise
