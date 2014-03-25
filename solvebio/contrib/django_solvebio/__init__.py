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

    # Override the SolveBio API host [OPTIONAL]
    SOLVEBIO_API_HOST = 'https://api.solvebio.com'

    # Use a custom dataset alias model by specifying it here [OPTIONAL]
    SOLVEBIO_DATASET_MODEL = 'django_solvebio.Dataset'

    # You can optionally bypass DB lookups by hardcoding aliases.
    # The key is the alias, and the value may be an ID or
    # full dataset name (see example below). [OPTIONAL]
    SOLVEBIO_DATASETS = {
        'clinvar': 'ClinVar/0.0.2/ClinVar'
    }


Support
-------

Feel free to submit issues to this GitHub repository and/or
send us an email at contact@solvebio.com.

"""
