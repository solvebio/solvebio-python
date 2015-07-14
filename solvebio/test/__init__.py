from __future__ import absolute_import
import pkgutil
import unittest

# FIXME: redo how testing works.


def all_names():
    for i, modname, j in pkgutil.iter_modules(__path__):
        if modname.startswith('test_'):
            yield 'solvebio.test.' + modname


def all():
    names = [name for name in all_names()]
    return unittest.defaultTestLoader.loadTestsFromNames(names)

# def unit():
#     unit_names = [name for name in all_names() if 'integration' not in name]
#     return unittest.defaultTestLoader.loadTestsFromNames(unit_names)
