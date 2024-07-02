![SolveBio Python Package](https://github.com/solvebio/solvebio-python/workflows/SolveBio%20Python%20Package/badge.svg)


SolveBio Python Client
======================

This is the SolveBio Python package and command-line interface (CLI).
This module is tested against Python 2.7, 3.6, 3.7, 3.8, 3.10, PyPy and PyPy3.

Developer documentation is available at [docs.solvebio.com](https://docs.solvebio.com). For more information about SolveBio visit [www.solvebio.com](https://www.solvebio.com).



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


Install from Git
----------------

    pip install -e git+https://github.com/solvebio/solvebio-python.git#egg=solve


Development
-----------

    git clone https://github.com/solvebio/solvebio-python.git
    cd solve-python/
    python setup.py develop


Or install `tox` and run:

    pip install tox
    tox


Releasing
---------

You will need to [configure Twine](https://twine.readthedocs.io/en/latest/#installation) in order to push to PyPI.

Maintainers can release solvebio-python to PyPI with the following steps:

    bumpversion <major|minor|patch>
    git push --tags
    make changelog
    make release



Support
-------

Developer documentation is available at [docs.solvebio.com](https://docs.solvebio.com).

If you experience problems with this package, please [create a GitHub Issue](https://github.com/solvebio/solvebio-python/issues).

For all other requests, please [email SolveBio Support](mailto:support@solvebio.com).


Configuring the Client
-------

The SolveBio python client can be configured by setting system environment variables.
Supported environment variables are:

`SOLVEBIO_API_HOST`     
- The URL of the target API backend. 
If not specified the value from the local credentials file will be used.

`SOLVEBIO_ACCESS_TOKEN` 
- The OAuth2 access token for authenticating with the API.

`SOLVEBIO_API_KEY`       
- The API Key to use for authenticating with the API.

The lookup order for credentials is:
1. Access Token
2. API Key
3. Local Credentials file

`SOLVEBIO_LOGLEVEL` 
- The log level at which to log messages.
If not specified the default log level will be WARN.

`SOLVEBIO_LOGFILE`        
- The file in which to write log messages. 
If the file does not exist it will be created. 
If not specified '~/.solvebio/solvebio.log' will be used by default.

`SOLVEBIO_RETRY_ALL`
- Flag for enabling aggressive retries for failed requests to the API.
When truthy, the client will attempt to retry a failed request regardless of the type of operation.
This includes idempotent and nonidempotent operations:
"HEAD", "GET", "PUT", "POST", "PATCH", "DELETE", "OPTIONS", "TRACE"
If this value is not set it will default to false and retries will only be enabled for idempotent operations.
