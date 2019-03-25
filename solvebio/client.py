# -*- coding: utf-8 -*-
from __future__ import absolute_import

import json
import time
import inspect

import solvebio

from .version import VERSION
from .errors import SolveError
from .utils.validators import validate_api_host_url

import platform
import requests
import textwrap
import logging

from requests import Session
from requests import codes
from requests.auth import AuthBase
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from six.moves.urllib.parse import urljoin

# Try using pyopenssl if available.
# Requires: pip install pyopenssl ndg-httpsclient pyasn1
# See http://urllib3.readthedocs.org/en/latest/contrib.html#module-urllib3.contrib.pyopenssl  # noqa
try:
    import urllib3.contrib.pyopenssl
    urllib3.contrib.pyopenssl.inject_into_urllib3()
except ImportError:
    pass

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
        if str(e):
            err += " with error message %s" % (str(e),)
        else:
            err += " with no error message"
    msg = textwrap.fill(msg) + "\n\n(Network error: %s)" % (err,)
    raise SolveError(message=msg)


class SolveTokenAuth(AuthBase):
    """Custom auth handler for SolveBio API token authentication"""

    def __init__(self, token=None, token_type='Token'):
        self.token = token
        self.token_type = token_type

        if not self.token:
            # Prefer the OAuth2 access token over the API key.
            if solvebio.access_token:
                self.token_type = 'Bearer'
                self.token = solvebio.access_token
            elif solvebio.api_key:
                self.token_type = 'Token'
                self.token = solvebio.api_key

    def __call__(self, r):
        if self.token:
            r.headers['Authorization'] = '{0} {1}'.format(self.token_type,
                                                          self.token)
        return r

    def __repr__(self):
        if self.token:
            return self.token_type
        else:
            return 'Anonymous'


class SolveClient(object):
    """A requests-based HTTP client for SolveBio API resources"""

    def __init__(self, host=None, token=None, token_type='Token',
                 include_resources=True):
        self.set_host(host)
        self.set_token(token, token_type)
        self._headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip,deflate',
            'User-Agent': 'SolveBio Python Client %s [Python %s/%s]' % (
                VERSION,
                platform.python_implementation(),
                platform.python_version()
            )
        }

        # Use a session with a retry policy to handle
        # intermittent connection errors.
        retries = Retry(
            total=5,
            backoff_factor=0.1,
            status_forcelist=[
                codes.bad_gateway,
                codes.service_unavailable,
                codes.gateway_timeout
            ])
        adapter = HTTPAdapter(max_retries=retries)
        self._session = Session()
        self._session.mount(self._host, adapter)

        # Import all resources into the client
        if include_resources:
            skip = ('SolveError', 'SolveClient',)
            for name, class_ in inspect.getmembers(solvebio, inspect.isclass):
                if name in skip:
                    continue
                subclass = type(name, (class_,), {'_client': self})
                setattr(self, name, subclass)

    def set_host(self, host=None):
        self._host = host or solvebio.api_host
        validate_api_host_url(self._host)

    def set_token(self, token=None, token_type='Token'):
        self._auth = SolveTokenAuth(token, token_type)

    def whoami(self):
        try:
            return self.get('/v1/user', {})
        except:
            return None

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

        return response.json()

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
