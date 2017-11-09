from __future__ import absolute_import

import json
import flask
import requests

try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

from .oauth import OAuthBase

import solvebio


class SolveBioAuth(OAuthBase):
    """Handles OAuth2 flows with the SolveBio API."""
    AUTH_COOKIE_NAME = 'dash_solvebio_auth'
    TOKEN_COOKIE_NAME = 'solvebio_oauth_token'

    OAUTH2_TOKEN_URL = urljoin(
        solvebio.api_host, '/v1/oauth2/token')
    OAUTH2_REVOKE_TOKEN_URL = urljoin(
        solvebio.api_host, '/v1/oauth2/revoke_token')
    DEFAULT_SOLVEBIO_URL = 'https://my.solvebio.com'
    DEFAULT_GRANT_TYPE = 'authorization_code'

    def __init__(self, app, app_url, client_id, **kwargs):
        super(SolveBioAuth, self).__init__(app, app_url, client_id)

        # Add logout URL
        app.server.add_url_rule(
            '{}_dash-logout'.format(app.config['routes_pathname_prefix']),
            view_func=self.logout,
            methods=['get']
        )

        # Handle optional parameters
        self._oauth_client_secret = kwargs.get('client_secret')
        self._solvebio_url = \
            kwargs.get('solvebio_url') or self.DEFAULT_SOLVEBIO_URL
        self._oauth_grant_type = \
            kwargs.get('grant_type') or self.DEFAULT_GRANT_TYPE
        if self._oauth_grant_type == 'implicit':
            self._oauth_response_type = 'token'
        elif self._oauth_grant_type == 'authorization_code':
            self._oauth_response_type = 'code'
        else:
            raise Exception(
                'SolveBioAuth Error: Unsupported grant type "{}"'
                .format(self._oauth_grant_type))

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
            'oauth_state': self._access_codes['access_granted'],
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
            redirect_uri = urljoin(
                flask.request.url_root,
                '{}_oauth-redirect'.format(
                    self._app.config['requests_pathname_prefix']))

            # Request the access token with the auth code
            oauth_data = requests.post(
                self.OAUTH2_TOKEN_URL,
                data={
                    'client_id': self._oauth_client_id,
                    'grant_type': self._oauth_grant_type,
                    'redirect_uri': redirect_uri,
                    'code': auth_code
                }).json()
        else:
            raise Exception(
                'SolveBio Auth Error: unsupported grant type "{}"'
                .format(self._oauth_grant_type))

        # Implicit flow returns the access_token in the initial redirect.
        # TODO: Support refresh tokens for authorization code flow.
        oauth_token = oauth_data['access_token']
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
            max_age=None
        )

        return response

    def logout(self):
        """Revoke the token and remove the cookie."""
        if self._oauth_client_secret:
            try:
                oauth_token = flask.request.cookies[self.TOKEN_COOKIE_NAME]
                # Revoke the token
                requests.post(
                    self.OAUTH2_REVOKE_TOKEN_URL,
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
