from __future__ import absolute_import

import json
import flask
import requests
import os

from six.moves.urllib.parse import urljoin

from dash_auth.oauth import OAuthBase

import solvebio


class SolveBioAuth(OAuthBase):
    """Handles OAuth2 flows with the SolveBio API."""
    AUTH_COOKIE_NAME = 'dash_solvebio_auth'
    TOKEN_COOKIE_NAME = 'solvebio_oauth_token'

    DEFAULT_TOKEN_COOKIE_MAX_AGE = 60 * 60 * 24 * 7
    DEFAULT_SOLVEBIO_URL = 'https://my.solvebio.com'
    DEFAULT_GRANT_TYPE = 'authorization_code'

    OAUTH2_TOKEN_PATH = '/v1/oauth2/token'
    OAUTH2_REVOKE_TOKEN_PATH = '/v1/oauth2/revoke_token'

    def __init__(self, app, app_url, client_id, **kwargs):
        secret_key = kwargs.get('secret_key') or app.server.secret_key
        super(SolveBioAuth, self).__init__(
            app,
            app_url,
            client_id,
            secret_key=secret_key,
            salt=kwargs.get('salt'))

        # Add logout URL
        app.server.add_url_rule(
            '{}_dash-logout'.format(app.config['routes_pathname_prefix']),
            view_func=self.logout,
            methods=['get']
        )

        self._oauth_redirect_uri = urljoin(
            self._app_url,
            '{}_oauth-redirect'.format(
                self._app.config['requests_pathname_prefix']))

        # Handle optional parameters
        self._solvebio_url = \
            kwargs.get('solvebio_url') or self.DEFAULT_SOLVEBIO_URL
        self._api_host = kwargs.get('api_host') or solvebio.api_host
        self._oauth_client_secret = kwargs.get('client_secret')
        self._oauth_grant_type = \
            kwargs.get('grant_type') or self.DEFAULT_GRANT_TYPE
        self.token_cookie_max_age = kwargs.get(
            'max_age', self.DEFAULT_TOKEN_COOKIE_MAX_AGE)

        if self._oauth_grant_type == 'implicit':
            self._oauth_response_type = 'token'
        elif self._oauth_grant_type == 'authorization_code':
            self._oauth_response_type = 'code'
        else:
            raise Exception(
                'SolveBioAuth Error: Unsupported grant type "{}"'
                .format(self._oauth_grant_type))

        _current_path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(_current_path, 'oauth-redirect.js'), 'r') as f:
            self.oauth_redirect_bundle = f.read()

        with open(os.path.join(_current_path, 'login.js'), 'r') as f:
            self.login_bundle = f.read()

    def auth_wrapper(self, f):
        def wrap(*args, **kwargs):
            if not self.is_authorized():
                # NOTE: We always show the login view instead of
                #       returning 403.
                # TODO - Add a list of valid app paths so we don't
                #        show the login page on asset URLs and Dash endpoints.
                return self.login_request()

            try:
                response = f(*args, **kwargs)
            except Exception as err:
                # Clear the cookie if auth fail
                if getattr(err, 'status_code', None) in [401, 403]:
                    response = flask.Response(status=403)
                    self.clear_cookies(response)
                    return response
                else:
                    raise

            # TODO - should set secure in this cookie, not exposed in flask
            # TODO - should set path or domain
            return self.add_access_token_to_response(response)

        # Support for dash-auth >= 1.0.0
        if hasattr(self, 'add_access_token_to_response'):
            return wrap
        else:
            return super(SolveBioAuth, self).auth_wrapper(f)

    def html(self, script):
        return ('''
            <!doctype html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Log In</title>
            </head>
            <body>
              <div id="react-root"></div>
            </body>
            <script id="_auth-config" type="application/json">
            {}
            </script>
            <script type="text/javascript">{}</script>
            </html>
        '''.format(json.dumps({
            'oauth_client_id': self._oauth_client_id,
            'oauth_response_type': self._oauth_response_type,
            'solvebio_url': self._solvebio_url,
            'requests_pathname_prefix':
            self._app.config['requests_pathname_prefix']
        }), script))

    def check_view_access(self, oauth_token):
        client = solvebio.SolveClient(token=oauth_token, token_type='Bearer')
        try:
            client.User.retrieve()
            return True
        except:
            return False

    def login_api(self):
        oauth_data = flask.request.get_json()

        if self._oauth_grant_type == 'authorization_code':
            # Authorization Code flow
            auth_code = oauth_data['code']

            # Request the access token with the auth code
            oauth_data = requests.post(
                urljoin(self._api_host, self.OAUTH2_TOKEN_PATH),
                data={
                    'client_id': self._oauth_client_id,
                    'grant_type': self._oauth_grant_type,
                    'redirect_uri': self._oauth_redirect_uri,
                    'code': auth_code
                }).json()
        else:
            raise Exception(
                'SolveBio Auth Error: unsupported grant type "{}"'
                .format(self._oauth_grant_type))

        # Implicit flow returns the access_token in the initial redirect.
        # TODO: Support refresh tokens for authorization code flow.
        oauth_token = oauth_data.get('access_token')
        if not oauth_token:
            # Return the error response to the frontend view
            return flask.Response(
                json.dumps(oauth_data),
                mimetype='application/json',
                status=500
            )

        client = solvebio.SolveClient(token=oauth_token, token_type='Bearer')
        user = client.User.retrieve()
        response = flask.Response(
            json.dumps(user),
            mimetype='application/json',
            status=200
        )

        self.set_cookie(
            response=response,
            name=self.TOKEN_COOKIE_NAME,
            value=oauth_token,
            max_age=self.token_cookie_max_age,
            samesite='Lax'
        )

        return response

    def logout(self):
        """Revoke the token and remove the cookie."""
        if self._oauth_client_secret:
            try:
                oauth_token = flask.request.cookies[self.TOKEN_COOKIE_NAME]
                # Revoke the token
                requests.post(
                    urljoin(self._api_host, self.OAUTH2_REVOKE_TOKEN_PATH),
                    data={
                        'client_id': self._oauth_client_id,
                        'client_secret': self._oauth_client_secret,
                        'token': oauth_token
                    })
            except:
                pass

        response = flask.redirect('/')
        self.clear_cookies(response)
        return response
