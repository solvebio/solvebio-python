"""Provides a helper function to query aliased datasets"""
from django.db.models.loading import get_model

import app_settings
DatasetModel = get_model(*app_settings.DATASET_MODEL.split('.'))


def query(alias, filters=[], fail_silently=False):
    """
    Wraps the SolveBio query API by aliasing datasets.
    Accepts a list of filters and returns a Query object.

    If fail_silently is True, the function returns None on:

        * error retrieving the dataset for a given alias,
        * query failure

    """
    try:
        dataset = DatasetModel.objects.get(alias=alias)
    except DatasetModel.DoesNotExist:
        if fail_silently:
            return None
        raise

    return dataset.query(filters, fail_silently)
