"""
Copyright (c) 2013 `Solve, Inc. <http://www.solvebio.com>`_.  All rights reserved.
"""
from setuptools import setup

__version__ = 'undefined'
for row in open('solve/__init__.py').readlines():
    if row.startswith('__version__'):
        exec(row)

setup(
    name='solve',
    version=__version__,
    description='The Solve bioinformatics working environment.',
    long_description=open('README.txt').read(),
    author='Solve, Inc.',
    author_email='help@solvebio.com',
    url='http://www.solvebio.com',
    license='MIT',
    packages=['solve'],
    # install_requires=[],
    platforms='any',
    entry_points={
        'console_scripts': ['solve = solve.core.cli.main:main']
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
    ],
)
