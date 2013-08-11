import sys
import requests
from requests.auth import AuthBase

from .credentials import get_credentials
from . import API_HOST


class SolveTokenAuth(AuthBase):
    """Custom auth handler for Solve API token authentication"""
    def __init__(self, token=None):
        self.token = token
        if self.token is None:
            # returns email,key if logged-in
            creds = get_credentials()
            if creds:
                self.token = creds[1]

    def __call__(self, r):
        if self.token:
            r.headers['Authorization'] = 'Token %s' % self.token
        return r


class SolveClient(object):
    def __init__(self, use_ssl=False):
        # self.session = requests.Session()
        self.proto = ('http', 'https')[use_ssl]
        self.api_host = '%s://%s' % (self.proto, API_HOST)
        self.auth = SolveTokenAuth()

    def _request(self, method, path, data={}, params={}):
        if not path.startswith('/'):
            path = '/%s' % path

        resp = requests.request(method=method, url=self.api_host + path,
                                params=params, data=data, auth=self.auth,
                                stream=False, verify=True)
        if resp.status_code in range(200, 210):
            return resp
        else:
            # Not OK
            try:
                body = resp.json()
                if u'non_field_errors' in body:
                    for i in body['non_field_errors']:
                        print i
            except:
                pass

            return None

        return resp

    def post_login(self, email, password):
        """Get a auth token for the given user credentials"""
        data = {
            'email': email,
            'password': password
        }

        return self._request('POST', '/auth/token/', data=data)

    def post_signup(self, email, password):
        data = {
            'email': email,
            'password': password
        }

        return self._request('POST', '/user/signup/', data=data)

    def get_current_user(self):
        return self._request('GET', '/user/current/')
