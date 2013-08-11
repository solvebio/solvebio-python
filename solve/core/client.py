import requests
from requests.auth import AuthBase

from .solvelog import solvelog
from .credentials import get_api_key
from . import API_HOST


class SolveAPIError(BaseException):
    pass


class SolveTokenAuth(AuthBase):
    """Custom auth handler for Solve API token authentication"""
    def __init__(self, token=None):
        self.token = token or get_api_key()

    def __call__(self, r):
        if self.token:
            r.headers['Authorization'] = 'Token %s' % self.token
        return r


class SolveClient(object):
    def __init__(self, use_ssl=False):
        # self.session = requests.Session()
        self.proto = ('http', 'https')[use_ssl]
        self.api_host = '%s://%s' % (self.proto, API_HOST)

    def _request(self, method, path, data={}, params={}):
        if not path.startswith('/'):
            path = '/%s' % path

        solvelog.debug('API %s Request: %s' % (method.upper(), path))
        resp = requests.request(method=method, url=self.api_host + path,
                                params=params, data=data,
                                auth=SolveTokenAuth(),
                                stream=False, verify=True)

        solvelog.debug('API Response: %d' % resp.status_code)
        if resp.status_code not in range(200, 210):
            raise SolveAPIError(self._get_error_message(resp))

        return resp.json()

    def _get_error_message(self, response):
        try:
            body = response.json()
        except:
            solvelog.error('API Error: no JSON response.')
        else:
            if u'non_field_errors' in body:
                return '\n'.join(body['non_field_errors'])
            elif u'detail' in body:
                return body['detail']
            else:
                solvelog.error('API Error response: ' + str(body))

        return ''

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
