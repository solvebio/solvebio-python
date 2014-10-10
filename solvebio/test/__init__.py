import pkgutil
import unittest

# FIXME: redo how testing works.

def all_names():
    for _, modname, _ in pkgutil.iter_modules(__path__):
        # FIXME: figure out why test loader can't resolve
        # solvebio.test.test_conversion
        if modname == 'test_conversion':
            continue
        if modname.startswith('test_modify_'):
            continue
        if modname.startswith('test_'):
            yield 'solvebio.test.' + modname


def all():
     return unittest.defaultTestLoader.loadTestsFromNames(all_names())

# def unit():
#     unit_names = [name for name in all_names() if 'integration' not in name]
#     return unittest.defaultTestLoader.loadTestsFromNames(unit_names)
