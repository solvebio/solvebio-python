# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

VERSION = 'undefined'
for row in open('solvebio/version.py').readlines():
    if row.startswith('VERSION'):
        exec(row)

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
    install_requires=['requests>=2.0.0'],
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
)
