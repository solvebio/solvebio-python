# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from setuptools import setup, find_packages

import sys
import warnings

VERSION = 'undefined'
install_requires = ['six', 'pyprind']
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


# solvebio-recipes requires additional packages
recipes_requires = [
    'pyyaml==5.3.1',
    'click==7.1.2',
    'ruamel.yaml==0.16.12'
]
extras_requires = {
    "recipes": recipes_requires
}

# Adjustments for Python 2 vs 3
if sys.version_info < (3, 0):
    # Get simplejson if we don't already have json
    try:
        import json  # noqa
    except ImportError:
        install_requires.append('simplejson')

    # solvebio-recipes only available in python3
    extras_requires = {}

with open('README.md') as f:
    long_description = f.read()

setup(
    name='solvebio',
    version=VERSION,
    description='The SolveBio Python client',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.8',
    author='Solve, Inc.',
    author_email='contact@solvebio.com',
    url='https://github.com/solvebio/solvebio-python',
    packages=find_packages(),
    package_dir={'solvebio': 'solvebio', 'recipes': 'recipes'},
    test_suite='solvebio.test',
    include_package_data=True,
    install_requires=install_requires,
    platforms='any',
    extras_require=extras_requires,
    entry_points={
        'console_scripts': ['solvebio = solvebio.cli.main:main',
                            'solvebio-recipes = recipes.sync_recipes:sync_recipes']
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
