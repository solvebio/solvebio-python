# -*- coding: utf-8 -*-
"""
django_solvebio
===============

Integrates the SolveBio Python client into Django.
This module makes it easier to integrate SolveBio into your Django project.
It provides a way to manage dataset versions by creating local aliases.


Requirements
------------

This module supports Django 1.4 and up. Python 3.0+ is not yet supported.
See the requirements for the `solvebio` Python module.


Installation
------------

Add `django_solvebio` to your `INSTALLED_APPS`:


    INSTALLED_APPS = (
        ...,
        'solvebio.contrib.django_solvebio',
    )


See your account page (https://www.solvebio.com/account) to get your API key.
Add your SolveBio API key to your ``settings.py``:


    SOLVEBIO_API_KEY = os.environ.get("SOLVEBIO_API_KEY", "YOUR API KEY")


Optional settings:

    # Add SolveBio Application credentials
    SOLVEBIO_APP_ID = os.environ.get("SOLVEBIO_APP_ID")
    SOLVEBIO_APP_SECRET = os.environ.get("SOLVEBIO_APP_SECRET")

    # Override the SolveBio API host [OPTIONAL]
    SOLVEBIO_API_HOST = 'https://api.solvebio.com'

    # You can optionally bypass DB lookups by hardcoding aliases.
    # The key is the alias, and the value may be an ID or
    # full dataset name (see example below). [OPTIONAL]
    SOLVEBIO_DATASET_ALIASES = {
        'clinvar': 'ClinVar/0.0.2/ClinVar'
    }


Support
-------

Feel free to submit issues to this GitHub repository and/or
send us an email at contact@solvebio.com.

"""
from __future__ import absolute_import
import re
import logging
import six
logger = logging.getLogger('django_solvebio')

from solvebio.resource import Dataset
from solvebio.errors import SolveError
from .models import DatasetAlias
from . import app_settings


class SolveBio(object):
    @classmethod
    def is_enabled(cls):
        return bool(app_settings.API_KEY)

    @classmethod
    def get_dataset(cls, alias):
        assert alias, 'Dataset alias argument cannot be None'

        if alias in app_settings.DATASET_ALIASES:
            return Dataset(app_settings.DATASET_ALIASES[alias])

        try:
            return Dataset(DatasetAlias.objects.get(alias=alias).dataset_id)
        except DatasetAlias.DoesNotExist:
            pass

        # if the alias_or_id matches the Dataset regex, return it
        if isinstance(alias, six.integer_types) or \
                re.match(Dataset.FULL_NAME_REGEX, alias):
            return Dataset(alias)

        raise SolveError(
            'Cannot find the SolveBio dataset by alias "%s"' % alias)
