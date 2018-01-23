[![Build Status](https://travis-ci.org/solvebio/solvebio-python.svg?branch=master)](http://travis-ci.org/solvebio/solvebio-python)


SolveBio Python Client
======================

This is the SolveBio Python package and command-line interface (CLI).
This module has been tested on Python 2.6+, Python 3.1+ and PyPy.

This version of the Python Client is compatible with Vault-based datasets
only (released on July 28th, 2017).

Developer documentation is available at [docs.solvebio.com](https://docs.solvebio.com). For more information about SolveBio visit [www.solvebio.com](https://www.solvebio.com).


Dependencies (Ubuntu)
--------------------

When installing SolveBio on Ubuntu (version 14 and up), you may need the
following dependencies:

* libgnutls-dev
* libcurl4-gnutls-dev

To install them, run:

    sudo apt-get install libcurl4-gnutls-dev libgnutls-dev


Installation & Setup
--------------------

Install `solvebio` using `pip`:

    pip install solvebio


For interactive use, we recommend installing `IPython` and `gnureadline`:

    pip install ipython
    pip install gnureadline


To log in, type:

    solvebio login


Enter your SolveBio credentials and you should be good to go!


Automatic Installer (Python 2.x only)
-------------------------------------

NOTE: The following installer works for Python 2.x only.

Open your terminal and paste the following command:

    curl -skL install.solvebio.com/python | bash


Install from Git
----------------

    pip install -e git+https://github.com/solvebio/solvebio-python.git#egg=solve


Development
-----------

    git clone https://github.com/solvebio/solvebio-python.git
    cd solve-python/
    python setup.py develop

To run tests use `nosetest`:

    nosetests solvebio.test.test_dataset


Or install `tox` and run:

    pip install tox
    tox


Support
-------

Developer documentation is available at [docs.solvebio.com](https://docs.solvebio.com).

If you experience problems with this package, please [create a GitHub Issue](https://github.com/solvebio/solvebio-python/issues).

For all other requests, please [email SolveBio Support](mailto:support@solvebio.com).
