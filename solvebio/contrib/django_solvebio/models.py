from __future__ import absolute_import
from django.db import models


class DatasetAlias(models.Model):
    """
    Stores local aliases to SolveBio dataset IDs.

    These aliases are overridden by the SOLVEBIO_DATASET_ALIASES settin.
    """

    alias = models.CharField(
        unique=True, db_index=True, max_length=100,
        help_text=("A local alias used to reference a versioned dataset"))

    dataset_id = models.CharField(
        max_length=100,
        help_text=("Can be an integer ID or a full name "
                   "(i.e. ClinVar/0.0.2/ClinVar)"))

    class Meta:
        verbose_name = "Dataset Alias"
        verbose_name_plural = "Dataset Aliases"
        ordering = ['alias']
