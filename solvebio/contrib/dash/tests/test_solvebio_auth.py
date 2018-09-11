from __future__ import absolute_import
import unittest
import dash
import dash_html_components as html
import time
import six
from six.moves import http_cookies
from six import iteritems

from solvebio.contrib.dash import SolveBioAuth

from .credentials import OAUTH_CLIENT_ID
from .credentials import OAUTH_TOKEN

if six.PY3:
    from unittest import mock
else:
    import mock  # noqa

endpoints = {
    'protected': {
        'get': [
            '/_dash-layout', '/_dash-routes', '/_dash-dependencies',
            '/_dash-component-suites/dash_html_components/bundle.js'
        ],
        'post': ['/_dash-update-component']
    },
    'unprotected': {
        'get': ['/'],
        'post': []
    }
}


def get_cookie(res, cookie_name):
    headers = res.headers.to_list()
    set_cookie_strings = [h for h in headers if (
        h[0] == 'Set-Cookie' and cookie_name in h[1]
    )]
    try:
        cookie_string = set_cookie_strings[0][1]
    except IndexError as e:
        print(cookie_name)
        for header in headers:
            print(header)
        print(set_cookie_strings)
        raise e

    cookie = http_cookies.SimpleCookie(cookie_string)
    access_granted_cookie = cookie[list(cookie.keys())[0]].value
    return access_granted_cookie


def create_apps(client_id):
    app_permissions = ['private']
    apps = dict((k, dash.Dash(k)) for k in app_permissions)
    for app in list(apps.values()):
        app.scripts.config.serve_locally = True
    auths = dict(
        (k, SolveBioAuth(
            apps[k],
            'http://localhost:5000',
            client_id,
            secret_key='test-secret-key',
            salt='test-salt'
        )) for k in app_permissions
    )
    apps['unregistered'] = dash.Dash('unregistered')
    apps['unregistered'].scripts.config.serve_locally = True
    return apps, auths


class ProtectedViewsTest(unittest.TestCase):
    def setUp(self):
        self._oauth_client_id = OAUTH_CLIENT_ID
        self._oauth_token = OAUTH_TOKEN
        self.longMessage = True

    def test_protecting_all_views(self):
        apps = create_apps(self._oauth_client_id)[0]
        self.assertEqual((
            len(endpoints['protected']['get']) +
            len(endpoints['unprotected']['get']) +
            len(endpoints['protected']['post']) +
            len(endpoints['unprotected']['post'])),
            # Subtract 1 for /<path> -> /<path:path>
            len([k for k in
                 apps['unregistered'].server.url_map.iter_rules()]) - 1
        )

    def test_unauthenticated_view(self):
        apps = create_apps(self._oauth_client_id)[0]
        for app_name in ['unregistered']:
            app = apps[app_name]
            app.layout = html.Div()
            client = app.server.test_client()
            for endpoint in (endpoints['protected']['get'] +
                             endpoints['unprotected']['get']):
                res = client.get(endpoint)
                test_name = '{} at {} ({})'.format(
                    res.status_code, endpoint, app_name
                )

                self.assertEqual(res.status_code, 200, test_name)

    def test_403_on_protected_endpoints_without_cookie(self):
        apps = create_apps(self._oauth_client_id)[0]
        for app in [apps['private']]:
            app.layout = html.Div()
            client = app.server.test_client()
            for endpoint in endpoints['protected']['get']:
                res = client.get(endpoint)
                self.assertEqual(res.status_code, 403, endpoint)

            for endpoint in endpoints['unprotected']['get']:
                res = client.get(endpoint)
                self.assertEqual(res.status_code, 200, endpoint)

            # TODO - check 200 on post of unprotected endpoints?
            for endpoint in endpoints['protected']['post']:
                res = client.post(endpoint)
                self.assertEqual(res.status_code, 403, endpoint)

    def check_endpoints(self, auth, app, oauth_token, cookies=tuple(),
                        all_200=False):
        def get_client():
            client = app.server.test_client()
            client.set_cookie(
                '/',
                'solvebio_oauth_token',
                oauth_token
            )
            for cookie in cookies:
                client.set_cookie('/', cookie['name'], cookie['value'])
            return client

        for endpoint in (endpoints['unprotected']['get'] +
                         endpoints['protected']['get']):
            client = get_client()  # use a fresh client for every endpoint
            res = client.get(endpoint)
            test_name = '{} at {} as {}'.format(
                res.status_code, endpoint, oauth_token
            )
            self.assertEqual(res.status_code, 200, test_name)
        return res

    def test_protected_endpoints_with_auth_cookie(self):
        apps, auths = create_apps(self._oauth_client_id)

        for app_name, app in iteritems(apps):
            if app_name != 'unregistered':
                app.layout = html.Div()
                self.check_endpoints(
                    auths[app_name],
                    app,
                    self._oauth_token
                )

    def test_auth_cookie_caches_calls_to_solvebio(self):
        app = dash.Dash()
        app.scripts.config.serve_locally = True
        auth = SolveBioAuth(
            app,
            'https://localhost:5000',
            self._oauth_client_id,
            secret_key='test-secret-key',
            salt='test-salt'
        )
        app.layout = html.Div()

        creator = self._oauth_token
        f = 'solvebio.contrib.dash.solvebio_auth.SolveBioAuth.check_view_access' # noqa
        with mock.patch(f, wraps=auth.check_view_access) as wrapped:
            self.check_endpoints(auth, app, creator)
            res = self.check_endpoints(auth, app, creator)

            n_endpoints = (
                len(endpoints['protected']['get']) +
                len(endpoints['unprotected']['get']))

            self.assertEqual(wrapped.call_count, n_endpoints * 2)

            access_granted_cookie = get_cookie(
                res,
                auth.AUTH_COOKIE_NAME)
            self.check_endpoints(auth, app, creator, (
                {'name': auth.AUTH_COOKIE_NAME,
                 'value': access_granted_cookie},
            ))
            self.assertEqual(wrapped.call_count, n_endpoints * 2)

            # Regenerate tokens with a shorter expiration
            # User's won't actually do this in practice, we're
            # just doing it to shorten up the expiration from 5 min
            # to 10 seconds
            auth.config['permissions_cache_expiry'] = 10
            auth.create_access_codes()
            res = self.check_endpoints(auth, app, creator)
            self.assertEqual(wrapped.call_count,
                             n_endpoints * 3)

            # Using the same auth cookie should prevent an
            # additional access call
            access_granted_cookie = get_cookie(
                res, auth.AUTH_COOKIE_NAME)
            self.check_endpoints(auth, app, creator, (
                {'name': auth.AUTH_COOKIE_NAME,
                 'value': access_granted_cookie},
            ))
            self.assertEqual(
                wrapped.call_count,
                (n_endpoints * 3))

            # But after the expiration time (10 seconds), another call to
            # SolveBio should be made
            time.sleep(10)
            self.check_endpoints(auth, app, creator)
            self.assertEqual(
                wrapped.call_count,
                (n_endpoints * 4))


class LoginFlow(unittest.TestCase):
    def login_success(self):
        oauth_client_id = OAUTH_CLIENT_ID
        oauth_token = OAUTH_TOKEN

        app = dash.Dash()
        app.config.scripts.serve_locally = True
        SolveBioAuth(
            app,
            'https://solvebio-dash-auth-app.herokuapp.com',
            oauth_client_id
        )
        app.layout = html.Div()
        client = app.server.test_client()
        csrf_token = get_cookie(client.get('/'), '_csrf_token')
        client.set_cookie('/', '_csrf_token', csrf_token)

        res = client.post('_login', headers={
            'Authorization': 'Bearer {}'.format(oauth_token),
            'X-CSRFToken': csrf_token
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            get_cookie(res, 'solvebio_oauth_token'),
            oauth_token
        )
