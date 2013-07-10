from setuptools import setup


setup(
    name='solve',
    version='0.0.1',
    description='The SolveBio bioinformatics working environment.',
    long_description=open('README.txt').read(),
    author='Solve, Inc.',
    author_email='help@solvebio.com',
    url='http://www.solvebio.com',
    license='MIT',
    packages=['solve', 'solve.cli'],
    # install_requires=[],
    platforms='any',
    entry_points={
        'console_scripts': ['solve = solve.cli.main:main']
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research'
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
    ],
)
