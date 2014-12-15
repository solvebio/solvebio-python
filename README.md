[![Build
Status](https://travis-ci.org/solvebio/solvebio-python.svg)](https://travis-ci.org/solvebio/solvebio-python)

SolveBio Python Client
======================

This is the SolveBio Python package and command-line interface (CLI).

For more information about SolveBio visit [solvebio.com](https://www.solvebio.com).


Guided Installation
-------------------

To use our guided installer, open up your terminal paste this:

    curl -kL install.solvebio.com/python | bash



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
