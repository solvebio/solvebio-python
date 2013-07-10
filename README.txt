SolveBio for Python
===================

The ```solve``` Python package and command-line interface (CLI)  are used to work in our bioinformatics environment.

For more information about SolveBio see <http://www.solvebio.com>.


Installation
------------

    pip install solve


Getting Started
---------------

```solvebio``` is our command-line tool. It is used to manage your credentials, etc...

Run ```solvebio setup``` on your command-line to walk-through the setup process.

    $ solvebio setup
    Enter your credentials.
    Email: curecancer@gmail.com
    Password (your typing will be hidden):
    Authentication failed/successful.

This process generates a new SolveBio API key and stores it in ```~/.solvebio/credentials```


See USAGE.md for more details.