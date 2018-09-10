# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from setuptools import setup, find_packages

import sys
import warnings

VERSION = 'undefined'
install_requires = ['six', 'pyprind', 'pycurl>=7.0.0']
extra = {}

with open('solvebio/version.py') as f:
    for row in f.readlines():
        if row.startswith('VERSION'):
            exec(row)

if sys.version_info < (2, 6):
    warnings.warn(
        'Python 2.5 is no longer officially supported by SolveBio. '
        'If you have any questions, please file an issue on GitHub or '
        'contact us at support@solvebio.com.',
        DeprecationWarning)
    install_requires.append('requests >= 0.8.8, < 0.10.1')
    install_requires.append('ssl')
elif sys.version_info < (2, 7):
    install_requires.append('ordereddict')
else:
    install_requires.append('requests>=2.0.0')

# Adjustments for Python 2 vs 3
if sys.version_info < (3, 0):
    # Get simplejson if we don't already have json
    try:
        import json  # noqa
    except ImportError:
        install_requires.append('simplejson')
else:
    extra['use_2to3'] = True

with open('README.md') as f:
    long_description = f.read()

try:
    setup(
        name='solvebio',
        version=VERSION,
        description='The SolveBio Python client',
        long_description=long_description,
        long_description_content_type='text/markdown',
        author='Solve, Inc.',
        author_email='contact@solvebio.com',
        url='https://github.com/solvebio/solvebio-python',
        packages=find_packages(),
        package_dir={'solvebio': 'solvebio'},
        test_suite='nose.collector',
        include_package_data=True,
        install_requires=install_requires,
        platforms='any',
        extras_require={},
        entry_points={
            'console_scripts': ['solvebio = solvebio.cli.main:main']
        },
        classifiers=[
            'Intended Audience :: Science/Research',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Scientific/Engineering :: Bio-Informatics'
        ],
        **extra
    )
except Exception as e:
    if 'Could not run curl-config' in str(e):
        print('\nProblem installing pycurl dependency'
              '\nYou probably need to install libcurl-devel '
              '(CentOS) or libcurl4-openssl-dev (Ubuntu)')
        sys.exit(1)
    else:
        raise
