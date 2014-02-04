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

        if response is not None:
            self.status_code = response.status_code
            try:
                self.json_body = response.json()
            except:
                logger.error(
                    'API Response (%d): No content.' % self.status_code)
            else:
                # log general errors before field errors
                if 'detail' in self.json_body:
                    logger.error(
                        'API Response (%d): %s'
                        % (self.status_code, self.json_body['detail']))
                    self.message = self.json_body['detail']

                if 'non_field_errors' in self.json_body:
                    [logger.error(i) for i in
                        self.json_body['non_field_errors']]

    def log_field_errors(self, fields):
        if self.json_body:
            for f in fields:
                if f in self.json_body:
                    logger.error('Field %s: %s' % (f, self.field_errors[f]))

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

    def request(self, method, url, params={}, data=None):
        if method.upper() in ('POST', 'PUT', 'PATCH'):
            data = json.dumps(data)

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

        if 200 <= response.status_code < 300:
            # all success responses are JSON
            return response.json()
        elif response.status_code == 401:
            # not authenticated
            raise SolveAPIError(
                message=LOGIN_REQUIRED_MESSAGE, response=response)
        elif response.status_code == 404:
            # not found
            raise SolveAPIError(
                message='Nothing was returned from that SolveBio API request',
                response=response)
        else:
            logger.debug('API Error: %d' % response.status_code)
            raise SolveAPIError(response=response)

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


    # def get_namespaces(self, page=1):
    #     try:
    #         # Only gets online Namespaces
    #         response = self._request(
    #             'GET', '/datasets?online=1&page=%d' % page)
    #     except SolveAPIError as err:
    #         if err.response.status_code == 404:
    #             return []
    #         raise err
    #     else:
    #         return response['results']

    # def get_namespace(self, namespace):
    #     return self._request('GET', '/datasets/%s' % namespace)

    # def get_dataset(self, namespace, dataset):
    #     return self._request('GET', '/datasets/%s/%s' % (namespace, dataset))

    # def get_dataset_field(self, namespace, dataset, field):
    #     return self._request('GET', '/datasets/%s/%s/fields/%s' % (namespace, dataset, field))

    # def post_dataset_select(self, namespace, dataset, data):
    #     return self._request('POST', '/datasets/%s/%s/_select' % (namespace, dataset),
    #                          data=data)

    # def get_dataset_select(self, namespace, dataset, scroll_id):
    #     return self._request('GET', '/datasets/%s/%s/_select' % (namespace, dataset),
    #                          params={'scroll_id': scroll_id})

    # def post_login(self, email, password):
    #     """Get an api_key for the given user credentials"""
    #     data = {
    #         'email': email,
    #         'password': password
    #     }
    #     try:
    #         return self._request('POST', '/auth/token', data=data)
    #     except SolveAPIError as exc:
    #         exc.log_field_errors(data.keys())
    #         return None

    # def get_current_user(self):
    #     try:
    #         return self._request('GET', '/user/current')
    #     except SolveAPIError:
    #         # TODO: handle invalid token
    #         return None



client = SolveClient()
