# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re

try:
    import json
except ImportError:
    json = None

# test for compatible json module
if not (json and hasattr(json, 'loads')):
    import simplejson as json  # noqa


def camelcase_to_underscore(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def class_to_api_name(name, pluralize=True):
    if pluralize:
        if name.endswith('y'):
            name = name[:-1] + 'ie'
        name = name + "s"

    return camelcase_to_underscore(name)
