[![Build Status](https://travis-ci.org/solvebio/solvebio-python.svg?branch=master)](http://travis-ci.org/solvebio/solvebio-python)


SolveBio Python Client
======================

This is the SolveBio Python package and command-line interface (CLI).
This module has been tested on Python 2.6+, Python 3.1+ and PyPy.

For more information about SolveBio visit [solvebio.com](https://www.solvebio.com).


Dependencies (Ubuntu)
--------------------

When installing SolveBio on Ubuntu (version 14 and up), you may need the
following dependencies:

* libgnutls-dev
* libcurl4-gnutls-dev

To install them, run:

    sudo apt-get install libcurl4-gnutls-dev libgnutls-dev


Guided Installation
-------------------

To use our guided installer, open up your terminal paste this:

    curl -skL install.solvebio.com/python | bash



Manual Installation
-------------------

You may want to first install `gnureadline` and `IPython`:

    pip install gnureadline
    pip install ipython


Install `solvebio` using `pip`:

    pip install solvebio


To log in, type:

    solvebio login

Enter your credentials and you should be good to go!

Just type `solvebio` to enter the SolveBio Python shell or `solvebio tutorial`
for a quick guide on using SolveBio.


Installing from Git
-------------------

    pip install -e git+https://github.com/solvebio/solvebio-python.git#egg=solve



Development
-----------

    git clone https://github.com/solvebio/solvebio-python.git
    cd solve-python/
    python setup.py develop

To run tests install tox and run that:

    pip install tox
    tox

To tag new versions:

    git tag `cat solvebio/version.py | cut -d "'" -f 2`
    git push --tags origin master
