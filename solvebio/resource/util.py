# -*- coding: utf-8 -*-
import re
import sys

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


def pluralize(name):
    if name.endswith('y'):
        name = name[:-1] + 'ie'
    return name + "s"


def class_to_api_name(name):
    return pluralize(camelcase_to_underscore(name))


def utf8(value):
    if isinstance(value, unicode) and sys.version_info < (3, 0):
        return value.encode('utf-8')
    return value
