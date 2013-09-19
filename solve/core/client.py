import platform
import requests
from requests.auth import AuthBase

from solve import __version__
from . import API_HOST
from .solvelog import solvelog
from .credentials import get_api_key


class SolveAPIError(BaseException):
    def __init__(self, response):
        self.response = response
        self.detail = None
        self.non_field_errors = []
        self.field_errors = {}

        try:
            body = response.json()
        except:
            solvelog.error('API Response (%d): No content.' % self.response.status_code)
        else:
            # log general errors before field errors
            if 'detail' in body:
                solvelog.error(self.detail)
                self.detail = body.pop('detail')

            if 'non_field_errors' in body:
                [solvelog.error(i) for i in body['non_field_errors']]
                self.non_field_errors = body.pop('non_field_errors')

            # Any remaining content are field-related errors
            self.field_errors = body

    def log_field_errors(self, fields):
        for f in fields:
            if f in self.field_errors:
                solvelog.error('Field %s: %s' % (f, self.field_errors[f]))


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

    def reset_auth(self, token=None):
        self.auth = SolveTokenAuth(token)

    def _request(self, method, path, data={}, params={}):
        if not path.startswith('/'):
            path = '/%s' % path

        solvelog.debug('API %s Request: %s' % (method.upper(), self.api_host + path))
        resp = requests.request(method=method, url=self.api_host + path,
                                params=params, data=data,
                                auth=self.auth,
                                stream=False, verify=True)

        if 200 <= resp.status_code < 300:
            # All success responses are JSON
            solvelog.debug('API Response: %d' % resp.status_code)
            return resp.json()
        else:
            # a fatal error! :-(
            solvelog.debug('API Error: %d' % resp.status_code)
            raise SolveAPIError(resp)

    def get_namespaces(self):
        # TODO: handle paginated namespace list
        namespaces = []
        response = self._request('GET', '/dataset/')
        namespaces += response['results']
        return namespaces

    def post_dataset_select(self, namespace, query):
        return self._request('POST', '/dataset/%s' % namespace, data=query)

    def post_login(self, email, password):
        """Get a auth token for the given user credentials"""
        data = {
            'email': email,
            'password': password
        }
        try:
            return self._request('POST', '/auth/token/', data=data)
        except SolveAPIError as exc:
            exc.log_field_errors(data.keys())
            return None

    def get_current_user(self):
        try:
            return self._request('GET', '/user/current/')
        except SolveAPIError:
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
        self._request('POST', '/report/install/', data=data)


client = SolveClient()
