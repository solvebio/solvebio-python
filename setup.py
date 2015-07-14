# -*- coding: utf-8 -*-
from __future__ import absolute_import
from setuptools import setup, find_packages

import sys
import warnings

VERSION = 'undefined'
for row in open('solvebio/version.py').readlines():
    if row.startswith('VERSION'):
        exec(row)


install_requires = ['six']

if sys.version_info < (2, 6):
    warnings.warn(
        'Python 2.5 is no longer officially supported by SolveBio. '
        'If you have any questions, please file an issue on GitHub or '
        'contact us at support@solvebio.com.',
        DeprecationWarning)
    install_requires.append('requests >= 0.8.8, < 0.10.1')
    install_requires.append('ssl')
else:
    install_requires.append('requests>=2.0.0')

# Adjustments for Python 2 vs 3
extra = {}

if sys.version_info < (3, 0):
    # Get simplejson if we don't already have json
    try:
        import json  # noqa
    except ImportError:
        install_requires.append('simplejson')
else:
    extra['use_2to3'] = True

setup(
    name='solvebio',
    version=VERSION,
    description='The SolveBio Python client',
    long_description=open('README.md').read(),
    author='Solve, Inc.',
    author_email='contact@solvebio.com',
    url='https://github.com/solvebio/solvebio-python',
    packages=find_packages(),
    package_dir={"solvebio": "solvebio"},
    test_suite='solvebio.test.all',
    include_package_data=True,
    install_requires=install_requires,
    platforms='any',
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
