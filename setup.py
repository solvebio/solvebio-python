# -*- coding: utf-8 -*-
#
# Copyright © 2013 Solve, Inc. <http://www.solvebio.com>. All rights reserved.
#
# email: contact@solvebio.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
    license="Apache License, Version 2.0",
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
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
    ],
)
