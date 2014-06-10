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
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip,deflate',
            'User-Agent': 'SolveBio Python Client %s [Python %s/%s]' % (
                version.VERSION,
                platform.python_implementation(),
                platform.python_version()
            )
        }

    def request(self, method, url, params=None, raw=False):
        if method.upper() in ('POST', 'PUT', 'PATCH'):
            # use only the data payload for write requests
            data = json.dumps(params)
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
            response = requests.request(method=method.upper(),
                                        url=url,
                                        params=params,
                                        data=data,
                                        auth=SolveTokenAuth(self._api_key),
                                        verify=True,
                                        timeout=80,
                                        headers=self.headers)
        except Exception as e:
            self._handle_request_error(e)

        if not (200 <= response.status_code < 300):
            self._handle_api_error(response)

        if raw:
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
