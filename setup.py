# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

__version__ = 'undefined'
for row in open('solvebio/__init__.py').readlines():
    if row.startswith('__version__'):
        exec(row)

setup(
    name='solvebio',
    version=__version__,
    description='The SolveBio Python client',
    long_description=open('README.txt').read(),
    author='Solve, Inc.',
    author_email='help@solvebio.com',
    url='http://www.solvebio.com',
    packages=find_packages(),
    package_dir={"solvebio": "solvebio"},
    #package_data={"solvebio": []},
    install_requires=['requests>=2.0.0', 'ipython'],
    platforms='any',
    entry_points={
        'console_scripts': ['solvebio = solvebio.core.cli.main:main']
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
    ],
)
