# -*- coding: utf-8 -*-
import solvebio
from solvebio import version
from solvebio.utils.printing import red
from solvebio.cli.credentials import get_credentials

import json
import platform
import requests
import textwrap
import logging
from urlparse import urljoin
from requests.auth import AuthBase

logger = logging.getLogger('solvebio')

LOGIN_REQUIRED_MESSAGE = red("""
Sorry, your API credentials seem to be invalid.

SolveBio is currently in Private Beta.
Please go to https://www.solvebio.com to find out more.

If you are a beta user, please log in by typing:

    solvebio login

""")


class SolveAPIError(BaseException):
    default_message = ('Unexpected error communicating with SolveBio. '
                       'If this problem persists, let us know at '
                       'contact@solvebio.com.')

    def __init__(self, message=None, response=None):
        self.json_body = None
        self.status_code = None
        self.message = message or self.default_message
        self.field_errors = []

        if response is not None:
            self.status_code = response.status_code
            try:
                self.json_body = response.json()
            except:
                if response.status_code == 404:
                    self.message = '404 Not Found.'
                logger.debug(
                    'API Response (%d): No content.' % self.status_code)
            else:
                logger.debug(
                    'API Response (%d): %s'
                    % (self.status_code, self.json_body))

                if self.status_code in [400, 404]:
                    self.message = 'Bad request.'

                    if 'detail' in self.json_body:
                        self.message = '%s.' % self.json_body['detail']

                    if 'non_field_errors' in self.json_body:
                        self.message = '%s.' % \
                            ', '.join(self.json_body['non_field_errors'])

                    for k, v in self.json_body.items():
                        if k not in ['detail', 'non_field_errors']:
                            if isinstance(v, list):
                                v = ', '.join(v)
                            self.field_errors.append('%s (%s)' % (k, v))

                    if self.field_errors:
                        self.message += (' The following fields were missing '
                                         'or invalid: %s' %
                                         ', '.join(self.field_errors))

    def __str__(self):
        return self.message


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
            creds = get_credentials()
            if creds:
                return creds[1]
        except:
            pass

        return None


class SolveClient(object):
    """A requests-based HTTP client for SolveBio API resources"""

    def __init__(self, api_key=None, api_host=None):
        self.api_key = api_key
        self.api_host = api_host
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

    def request(self, method, url, params=None):
        if method.upper() in ('POST', 'PUT', 'PATCH'):
            # use only the data payload for write requests
            data = json.dumps(params)
            params = None
        else:
            data = None

        api_host = self.api_host or solvebio.api_host
        if not api_host:
            raise SolveAPIError(message='No SolveBio API host is set')
        elif not url.startswith(api_host):
            url = urljoin(api_host, url)

        logger.debug('API %s Request: %s' % (method.upper(), url))

        try:
            response = requests.request(method=method.upper(),
                                        url=url,
                                        params=params,
                                        data=data,
                                        auth=SolveTokenAuth(self.api_key),
                                        verify=True,
                                        timeout=80,
                                        headers=self.headers)
        except Exception as e:
            self._handle_request_error(e)

        # TODO: get API version from response headers

        if not (200 <= response.status_code < 300):
            self._handle_api_error(response)
        else:
            # all success responses are JSON
            return response.json()

    def _handle_request_error(self, e):
        if isinstance(e, requests.exceptions.RequestException):
            msg = SolveAPIError.default_message
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
        raise SolveAPIError(message=msg)

    def _handle_api_error(self, response):
        if response.status_code in [400, 404]:
            raise SolveAPIError(response=response)
        elif response.status_code == 401:
            # not authenticated
            raise SolveAPIError(
                message=LOGIN_REQUIRED_MESSAGE, response=response)
        else:
            logger.info('API Error: %d' % response.status_code)
            raise SolveAPIError(response=response)

client = SolveClient()
