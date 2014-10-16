import pkgutil
import unittest

# FIXME: redo how testing works.


def all_names():
    for i, modname, j in pkgutil.iter_modules(__path__):
        print i, j
        print modname
        # FIXME: figure out why test loader can't resolve
        # solvebio.test.test_conversion
        # if modname in ('test_conversion',
        #                # 'test_annotation_access',
        #                # 'test_query',
        #                # 'test_query_batch',
        #                # 'test_query_paging',
        #                # 'test_sample_access',
        #                # 'test_sample',
        #                'test_annotation'):
        #     continue
        if modname.startswith('test_'):
            yield 'solvebio.test.' + modname


def all():
    names = [name for name in all_names()]
    return unittest.defaultTestLoader.loadTestsFromNames(names)

# def unit():
#     unit_names = [name for name in all_names() if 'integration' not in name]
#     return unittest.defaultTestLoader.loadTestsFromNames(unit_names)
