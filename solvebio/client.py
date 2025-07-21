# -*- coding: utf-8 -*-
from __future__ import absolute_import

import json
import time
import inspect
import os
from typing import Literal

import solvebio

from .version import VERSION
from .errors import SolveError
from .auth import authenticate, SolveBioTokenAuth

import platform
import requests
import textwrap
import logging

from requests import Session, codes, adapters
from requests.packages.urllib3.util.retry import Retry

import ssl
import sys

from six.moves.urllib.parse import urljoin

# Try using pyopenssl if available.
# Requires: pip install pyopenssl ndg-httpsclient pyasn1
# See http://urllib3.readthedocs.org/en/latest/contrib.html#module-urllib3.contrib.pyopenssl  # noqa
try:
    import urllib3

    if sys.version_info <= (3, 9):
        import urllib3.contrib.pyopenssl
    else:
        # Python 3.10+ automatically handles SSL; no need for inject_into_urllib3()
        pass
except ImportError:
    pass

# Ensure SSL/TLS support is available
if not ssl.HAS_TLSv1_2:
    raise RuntimeError("TLS 1.2 support is required but not available.")


logger = logging.getLogger('solvebio')


def _handle_api_error(response):
    if response.status_code not in [400, 401, 403, 404]:
        logger.info('API Error: %d' % response.status_code)
    raise SolveError(response=response)


def _handle_request_error(e):
    if isinstance(e, requests.exceptions.RequestException):
        msg = SolveError.default_message
        err = "%s: %s" % (type(e).__name__, str(e))
    else:
        msg = ("Unexpected error communicating with SolveBio.\n"
               "It looks like there's probably a configuration "
               "issue locally.\nIf this problem persists, let us "
               "know at support@solvebio.com.")
        err = "A %s was raised" % (type(e).__name__,)
        if isinstance(e, (urllib3.exceptions.SSLError, ssl.SSLError)) or sys.version_info >= (3, 12):
            err += ("\n\nThis is an SSLError. If you're using python 3.12, "
                    "it could be because of stricter SSL requirements:\n"
                    "https://docs.python.org/3/whatsnew/3.12.html\n"
                    "https://docs.python.org/3/whatsnew/3.12.html\n"
                    "Try upgrading urllib3 and certifi:\n"
                    "  pip install --upgrade urllib3 certifi\n\n")
        elif str(e):
            err += " with error message %s" % (str(e),)
        else:
            err += " with no error message"
    msg = textwrap.fill(msg) + "\n\n(Network error: %s)" % (err,)
    raise SolveError(message=msg)


class SolveClient(object):
    """A requests-based HTTP client for SolveBio API resources"""

    _host: str = None
    _auth: SolveBioTokenAuth = None

    def __init__(
        self,
        host=None,
        token=None,
        token_type: Literal["Bearer", "Token"] = "Token",
        include_resources=True,
        retry_all: bool = None,
    ):
        self._host: str = None
        self._auth: SolveBioTokenAuth = None
        self._session: Session = None

        self._headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip,deflate'
        }
        self.retry_all = bool(retry_all)
        if self.retry_all is None:
            self.retry_all = bool(os.environ.get("SOLVEBIO_RETRY_ALL"))

        # this class is created before any commands, so it shouldn't raise a missing host exception
        self.set_credentials(host, token, token_type, raise_on_missing=False)
        self.set_user_agent()

        # Import all resources into the client
        if include_resources:
            skip = ('SolveError', 'SolveClient',)
            for name, class_ in inspect.getmembers(solvebio, inspect.isclass):
                if name in skip:
                    continue
                subclass = type(name, (class_,), {'_client': self})
                setattr(self, name, subclass)

    def set_user_agent(self, name=None, version=None):
        ua = 'solvebio-python-client/{} python-requests/{} {}/{}'.format(
            VERSION,
            requests.__version__,
            platform.python_implementation(),
            platform.python_version()
        )

        # Prefix the name of the app or script before the
        # default user-agent.
        if name:
            name = name.replace(' ', '-')
            if version:
                ua = '{}/{} {}'.format(name, version, ua)
            else:
                ua = '{} {}'.format(name, ua)

        self._headers['User-Agent'] = ua

    def set_credentials(
        self, host: str, token: str, token_type: Literal["Bearer", "Token"],
        *, debug: bool = False, raise_on_missing: bool = True
    ):
        self._host, self._auth = authenticate(
            host, token, token_type, debug=debug, raise_on_missing=raise_on_missing
        )

        if self._host:
            retry_kwargs = {}
            if self.retry_all:
                logger.info("Retries enabled for all API requests")
                retry_kwargs["allow_redirects"] = frozenset(
                    ["HEAD", "GET", "PUT", "POST", "PATCH", "DELETE", "OPTIONS", "TRACE"]
                )
            else:
                logger.info("Retries enabled for read-only API requests")

            retries = Retry(
                total=5,
                backoff_factor=2,
                status_forcelist=[
                    codes.bad_gateway,
                    codes.service_unavailable,
                    codes.gateway_timeout,
                ],
                **retry_kwargs
            )

            # Use a session with a retry policy to handle
            # intermittent connection errors.
            adapter = adapters.HTTPAdapter(max_retries=retries)
            self._session = Session()
            self._session.mount(self._host, adapter)

    def is_logged_in(self):
        return bool(self._host and self._auth and self._session)

    def whoami(self):
        return self.get('/v1/user', {})

    def get(self, url, params, **kwargs):
        """Issues an HTTP GET across the wire via the Python requests
        library. See *request()* for information on keyword args."""
        kwargs['params'] = params
        return self.request('GET', url, **kwargs)

    def post(self, url, data, **kwargs):
        """Issues an HTTP POST across the wire via the Python requests
        library. See *request* for information on keyword args."""
        kwargs['data'] = data
        return self.request('POST', url, **kwargs)

    def delete(self, url, data, **kwargs):
        """Issues an HTTP DELETE across the wire via the Python requests
        library. See *request* for information on keyword args."""
        kwargs['data'] = data
        return self.request('DELETE', url, **kwargs)

    def request(self, method, url, **kwargs):
        """
        Issues an HTTP Request across the wire via the Python requests
        library.

        Parameters
        ----------

        method : str
           an HTTP method: GET, PUT, POST, DELETE, ...

        url : str
           the place to connect to. If the url doesn't start
           with a protocol (https:// or http://), we'll slap
                solvebio.api_host in the front.

        allow_redirects: bool, optional
           set *False* we won't follow any redirects

        headers: dict, optional

          Custom headers can be provided here; generally though this
          will be set correctly by default dependent on the
          method type. If the content type is JSON, we'll
          JSON-encode params.

        param : dict, optional
           passed as *params* in the requests.request

        timeout : int, optional
          timeout value in seconds for the request

        raw: bool, optional
          unless *True* the response encoded to json

        files: file
          File content in the form of a file handle which is to be
          uploaded. Files are passed in POST requests

        Returns
        -------
        response object. If *raw* is not *True* and
        repsonse if valid the object will be JSON encoded. Otherwise
        it will be the request.reposne object.
        """
        if not self.is_logged_in():
            raise SolveError("HTTP request: client is not logged in!")

        opts = {
            'allow_redirects': True,
            'auth': self._auth,
            'data': {},
            'files': None,
            'headers': dict(self._headers),
            'params': {},
            'timeout': 80,
            'verify': True
        }

        raw = kwargs.pop('raw', False)
        debug = kwargs.pop('debug', False)
        opts.update(kwargs)
        method = method.upper()

        if opts['files']:
            # Don't use application/json for file uploads or GET requests
            opts['headers'].pop('Content-Type', None)
        else:
            opts['data'] = json.dumps(opts['data'])

        if not url.startswith(self._host):
            url = urljoin(self._host, url)

        logger.debug('API %s Request: %s' % (method, url))

        if debug:
            self._log_raw_request(method, url, **opts)

        try:
            response = self._session.request(method, url, **opts)
        except Exception as e:
            _handle_request_error(e)

        if 429 == response.status_code:
            delay = int(response.headers['retry-after']) + 1
            logger.warn('Too many requests. Retrying in {0}s.'.format(delay))
            time.sleep(delay)
            return self.request(method, url, **kwargs)

        if not (200 <= response.status_code < 400):
            _handle_api_error(response)

        # 204 is used on deletion. There is no JSON here.
        if raw or response.status_code in [204, 301, 302]:
            return response

        try:
            return response.json()
        except Exception:
            if b"<!DOCTYPE html>" in response.content[:40]:
                helper_msg = self._host
                if suggested_host := self.validate_host_is_www_url(self._host):
                    helper_msg = f"Provided API host is: `{self._host}`. Did you perhaps mean `{suggested_host}`?"

                html_response = response.text[:30].replace("\n", "")
                raise SolveError(
                    f"QuartzBio error: HTML response received from API. {html_response}...\n"
                    "  Please confirm that API Host doesn't point to EDP's Web URL:\n"
                    f"  {helper_msg}"
                )
            elif self._host is None:
                # shouldn't happen, maybe in rare race conditions
                raise SolveError("No EDP API host was set!")

            raise SolveError(
                f"Could not parse JSON response: {response.content}"
            )

    def validate_host_is_www_url(self, host):
        # returns corrected API's URL, if it suspects that host is a WWW url, not API
        if ".api.edp" not in host and ".edp" in host:
            return host.replace(".edp", ".api.edp")

    def _log_raw_request(self, method, url, **kwargs):
        from requests import Request, Session
        req = Request(method=method.upper(), url=url,
                      data=kwargs['data'], params=kwargs['params'])
        prepped = Session().prepare_request(req, )
        logger.debug(prepped.headers)
        logger.debug(prepped.body)

    def __repr__(self):
        return '<SolveClient {0} {1}>'.format(self._host, self._auth)


client = SolveClient(include_resources=False)
