# -*- coding: utf-8 -*-
import solvebio
from solvebio import version
from solvebio.credentials import get_credentials
from solvebio.errors import SolveError

import json
import platform
import requests
import textwrap
import logging
from urlparse import urljoin
from requests.auth import AuthBase

logger = logging.getLogger('solvebio')


class SolveTokenAuth(AuthBase):
    """Custom auth handler for SolveBio API token authentication"""

    def __init__(self, token=None):
        self.token = token or self._get_api_key()

    def __call__(self, r):
        if self.token:
            r.headers['Authorization'] = 'Token %s' % self.token
        return r

    def __repr__(self):
        return u'<SolveTokenAuth %s>' % self.token

    def _get_api_key(self):
        """
        Helper function to get the current user's API key or None.
        """
        if solvebio.api_key:
            return solvebio.api_key

        try:
            return get_credentials()[1]
        except:
            pass

        return None


class SolveClient(object):
    """A requests-based HTTP client for SolveBio API resources"""

    def __init__(self, api_key=None, api_host=None):
        self._api_key = api_key
        self._api_host = api_host
        self._headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip,deflate',
            'User-Agent': 'SolveBio Python Client %s [Python %s/%s]' % (
                version.VERSION,
                platform.python_implementation(),
                platform.python_version()
            )
        }

    def request(self, method, url, params=None, raw=False,
                auth_class=SolveTokenAuth, timeout=80,
                files=None, headers={}):
        """
        Issues an HTTP Request across the wire via the Python requests
        library.
           * *method* is an HTTP method: GET, PUT, POST, DELETE, ...
           * *url* is the place to connect to. If the url doesn't start
             with a protocol (https:// or http://), we'll slap
             solvebio.api_host in the front.
          *  *params* will go into the parameters or data section of
             the request as appropriate, depending on the method value.
          *  *timeout* is a timeout value in seconds for the request
          *  File content in the form of a file handle can be passed
             in *files* to upload a file. Generally files are passed
             via POST requests
          *  Custom headers can be provided through the *headers*
             dictionary; generally though this will be set correctly by
             default dependent on the method type. If the content type
             is JSON, we'll JSON-encode params.
        """
        # Support auth-less requests (ie for OAuth2)
        if auth_class:
            _auth = auth_class(self._api_key)
        else:
            _auth = None

        # Support header modifications
        _headers = dict(self._headers)
        _headers.update(headers)

        if method.upper() in ('POST', 'PUT', 'PATCH'):
            # We use only data payload for write requests, set that up and
            # nuke params.
            if files is not None:
                # Don't use application/json for file uploads or GET requests
                _headers.pop('Content-Type', None)
                data = params
            elif _headers.get('Content-Type', None) == 'application/json':
                data = json.dumps(params)
            else:
                data = params
            params = None
        else:
            data = None

        api_host = self._api_host or solvebio.api_host

        if not api_host:
            raise SolveError(message='No SolveBio API host is set')
        elif not url.startswith(api_host):
            url = urljoin(api_host, url)

        logger.debug('API %s Request: %s' % (method.upper(), url))
        try:
            response = requests.request(
                method=method.upper(), url=url, params=params,
                data=data, verify=True, timeout=timeout,
                auth=_auth, headers=_headers, files=files)
        except Exception as e:
            self._handle_request_error(e)

        if not (200 <= response.status_code < 300):
            self._handle_api_error(response)

        # 204 is used on deletion. There is no JSON here.
        if raw or response.status_code == 204:
            return response

        return response.json()

    def _handle_request_error(self, e):
        if isinstance(e, requests.exceptions.RequestException):
            msg = SolveError.default_message
            err = "%s: %s" % (type(e).__name__, str(e))
        else:
            msg = ("Unexpected error communicating with SolveBio. "
                   "It looks like there's probably a configuration "
                   "issue locally. If this problem persists, let us "
                   "know at contact@solvebio.com.")
            err = "A %s was raised" % (type(e).__name__,)
            if str(e):
                err += " with error message %s" % (str(e),)
            else:
                err += " with no error message"
        msg = textwrap.fill(msg) + "\n\n(Network error: %s)" % (err,)
        raise SolveError(message=msg)

    def _handle_api_error(self, response):
        if response.status_code in [400, 401, 403, 404]:
            raise SolveError(response=response)
        else:
            logger.info('API Error: %d' % response.status_code)
            raise SolveError(response=response)

client = SolveClient()
