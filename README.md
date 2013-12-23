SolveBio Python Client
======================

The solve Python package and command-line interface (CLI) are used to work in our bioinformatics environment.

For more information about SolveBio see http://www.solvebio.com


Automatic Installer
-------------------

To use our guided installer, open up your terminal paste this:

    curl -kL install.solvebio.com | bash



Manual Installation
-------------------

You may want to first install `readline` for a better experience:

    easy_install readline


Now just install `solvebio` from PyPI:

    pip install solvebio


To log in, type:

    solvebio login

Enter your credentials and you should be good to go!
Just type `solvebio` to enter the SolveBio Python shell.


Installing from Git
-------------------

    pip install -e git+https://github.com/solvebio/solvebio-python.git#egg=solve



Development
-----------

    git clone https://github.com/solvebio/solvebio-python.git
    cd solve-python/
    python setup.py develop

