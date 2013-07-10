SolveBio for Python
===================

The SolveBio Python package ```solve``` and ```solvebio``` command-line app are used to work in our bioinformatics environment.

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


Importing Data
--------------

Load your local datasets that work with Solve importers:

* SQL
* CSV
* Known file formats?

This will let you access your data within the SolveBio Python environment. 


### Supported File Formats

*TBD*


The SolveBio Shell
------------------

Run ```solvebio shell``` to launch a SolveBio shell. The shell runs iPython and automatically imports the ```solve``` Python library.

    > solvebio shell
    In [1]: 


You can start working right away from the shell.


Querying SolveBio Databases
---------------------------

*TBD*


