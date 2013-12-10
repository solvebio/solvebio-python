# -*- coding: utf-8 -*-
#
# Copyright © 2013 Solve, Inc. <http://www.solvebio.com>. All rights reserved.
#
# email: contact@solvebio.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import json
import platform
import requests
from requests.auth import AuthBase

from solvebio import __version__
from .solvelog import solvelog
from .credentials import get_api_key
from .utils.printing import red

from .solveconfig import solveconfig

LOGIN_REQUIRED_MESSAGE = red("""
Sorry, your API credentials seem to be invalid.

SolveBio is currently in private beta.
Please go to www.solvebio.com to find out more.

If you are a beta user, please log in by typing:

    solvebio login

""")


class SolveAPIError(BaseException):
    def __init__(self, response):
        self.response = response
        self.body = None
        self.message = 'Server error, please try again later'

        try:
            self.body = response.json()
        except:
            solvelog.error('API Response (%d): No content.' % self.response.status_code)
        else:
            # log general errors before field errors
            if 'detail' in self.body:
                solvelog.error('API Response (%d): %s' % (self.response.status_code, self.body['detail']))
                self.message = self.body['detail']

            if 'non_field_errors' in self.body:
                [solvelog.error(i) for i in self.body['non_field_errors']]

    def log_field_errors(self, fields):
        for f in fields:
            if f in self.body:
                solvelog.error('Field %s: %s' % (f, self.field_errors[f]))

    def __str__(self):
        return self.message


class SolveTokenAuth(AuthBase):
    """Custom auth handler for SolveBio API token authentication"""
    def __init__(self, api_key=None):
        self.api_key = api_key or get_api_key()

    def __call__(self, r):
        if self.api_key:
            r.headers['Authorization'] = 'Token %s' % self.api_key
        return r

    def __repr__(self):
        return u'<SolveTokenAuth %s>' % self.api_key


class SolveClient(object):

    def __init__(self, api_key=None):
        # override the netrc credential by passing an api_key
        self.api_key = api_key
        # auth is lazy-loaded on first request
        self.auth = None
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'SolveBio Python Client %s [Python %s/%s]' % (
                __version__,
                platform.python_implementation(),
                platform.python_version()
            )
        }

    def _build_url(self, path):
        # TODO: not sure if this is the best way :-S
        if not path.startswith('/'):
            path = '/' + path
        return u'%s://%s' % (('http', 'https')[bool(solveconfig.API_SSL)],
                             solveconfig.API_HOST) + path

    def _request(self, method, path, params={}, data=None):
        url = self._build_url(path)

        if self.auth is None:
            self.auth = SolveTokenAuth(self.api_key)

        if method in ('POST', 'PUT'):
            data = json.dumps(data)
        else:
            data = None

        solvelog.debug('API %s Request: %s' % (method.upper(), url))
        response = requests.request(method=method.upper(),
                                    url=url,
                                    params=params,
                                    data=data,
                                    auth=self.auth,
                                    stream=False,
                                    verify=True,
                                    headers=self.headers)

        if 200 <= response.status_code < 300:
            # All success responses are JSON
            solvelog.debug('API Response: %d' % response.status_code)
            return response.json()
        elif response.status_code == 401:
            # not authenticated
            print LOGIN_REQUIRED_MESSAGE
            raise SolveAPIError(response)
        elif response.status_code != 404:
            solvelog.debug('API Error: %d' % response.status_code)

        raise SolveAPIError(response)

    def get_namespaces(self, page=1):
        try:
            # Only gets online Namespaces
            response = self._request('GET', '/datasets?online=1&page=%d' % page)
        except SolveAPIError as err:
            if err.response.status_code == 404:
                return []
            raise err
        else:
            return response['results']

    def get_namespace(self, namespace):
        return self._request('GET', '/datasets/%s' % namespace)

    def get_dataset(self, namespace, dataset):
        return self._request('GET', '/datasets/%s/%s' % (namespace, dataset))

    def post_dataset_select(self, namespace, data):
        return self._request('POST', '/datasets/%s/_select' % namespace,
                             data=data)

    def get_dataset_select(self, namespace, scroll_id):
        return self._request('GET', '/datasets/%s/_select' % namespace,
                             params={'scroll_id': scroll_id})

    def post_login(self, email, password):
        """Get an api_key for the given user credentials"""
        data = {
            'email': email,
            'password': password
        }
        try:
            return self._request('POST', '/auth/token', data=data)
        except SolveAPIError as exc:
            exc.log_field_errors(data.keys())
            return None

    def get_current_user(self):
        try:
            return self._request('GET', '/user/current')
        except SolveAPIError:
            # TODO: handle invalid token
            return None

    def post_install_report(self):
        data = {
            'hostname': platform.node(),
            'python_version': platform.python_version(),
            'python_implementation': platform.python_implementation(),
            'platform': platform.platform(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'pyexe_build': platform.architecture()[0]
        }
        self._request('POST', '/reports/install', data=data)


client = SolveClient()
