import platform
import requests
from requests.auth import AuthBase

from solve import __version__
from solve.core import API_HOST
from solve.core.solvelog import solvelog
from solve.core.credentials import get_api_key


class SolveAPIError(BaseException):
    error_message_fields = ['detail', 'non_field_errors']

    def __init__(self, response):
        self.response = response

        try:
            body = response.json()
        except:
            solvelog.error('API Response (%d): No content.' % self.response.status_code)
        else:
            # log general errors before field errors
            if 'detail' in body:
                solvelog.error(body['detail'])
            if 'non_field_errors' in body:
                for i in body['non_field_errors']:
                    solvelog.error(i)

            # TODO: standardize this into 'field_errors' key
            for i, msg in body.items():
                if i not in ['detail', 'non_field_errors']:
                    for j in msg:
                        solvelog.error('%s error: %s' % (i, j))


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
        self.auth = SolveTokenAuth()
        self.proto = ('http', 'https')[use_ssl]
        self.api_host = '%s://%s' % (self.proto, API_HOST)
        self.headers = {
            'Accept': 'application/json',
            'User-Agent': 'Solve Client %s [Python %s/%s]' % (
                __version__,
                platform.python_implementation(),
                platform.python_version()
            )
        }

    def _request(self, method, path, data={}, params={}):
        if not path.startswith('/'):
            path = '/%s' % path

        solvelog.debug('API %s Request: %s' % (method.upper(), self.api_host + path))
        resp = requests.request(method=method, url=self.api_host + path,
                                params=params, data=data,
                                auth=self.auth,
                                stream=False, verify=True)

        if 200 <= resp.status_code < 300:
            solvelog.debug('API Response: %d' % resp.status_code)
            # All success responses are JSON
            return resp.json()
        else:
            solvelog.debug('API Error: %d' % resp.status_code)
            raise SolveAPIError(resp)

    def post_dataset_select(self, dataset, query):
        return self._request('POST', '/dataset/%s', data=query)

    def post_login(self, email, password):
        """Get a auth token for the given user credentials"""
        data = {
            'email': email,
            'password': password
        }
        return self._request('POST', '/auth/token/', data=data)

    def get_current_user(self):
        return self._request('GET', '/user/current/')

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
        self._request('POST', '/report/install/', data=data)


client = SolveClient()
