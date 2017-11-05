from dash.dependencies import Input, Output
import dash
import dash_html_components as html
import dash_core_components as dcc
import time

from solvebio.contrib.dash import SolveBioAuth

from .IntegrationTests import IntegrationTests
from .utils import switch_windows

from .credentials import OAUTH_CLIENT_ID
from .credentials import OAUTH_USERNAME
from .credentials import OAUTH_PASSWORD
from .credentials import OAUTH_DOMAIN


class Tests(IntegrationTests):
    test_client_id = OAUTH_CLIENT_ID
    test_domain = OAUTH_DOMAIN
    test_username = OAUTH_USERNAME
    test_password = OAUTH_PASSWORD

    def solvebio_auth_login_flow(self, username, pw, domain,
                                 url_base_pathname):
        app = dash.Dash(__name__, url_base_pathname=url_base_pathname)
        app.layout = html.Div([
            dcc.Input(
                id='input',
                value='initial value'
            ),
            html.Div(id='output')
        ])

        @app.callback(Output('output', 'children'), [Input('input', 'value')])
        def update_output(new_value):
            return new_value

        SolveBioAuth(
            app,
            'http://localhost:8050{}'.format(url_base_pathname),
            self.test_client_id
        )

        self.startServer(app)

        time.sleep(10)
        self.percy_snapshot('login screen - {} {} {}'.format(
            username, pw, url_base_pathname))
        try:
            self.wait_for_element_by_id('dash-auth--login__container')
        except Exception as e:
            print(self.wait_for_element_by_tag_name('body').html)
            raise e

        self.driver.find_element_by_id('dash-auth--login__button').click()
        time.sleep(5)
        switch_windows(self.driver)

        # Domain selection
        time.sleep(5)
        self.wait_for_element_by_css_selector(
            'input[name="domain"]'
        ).send_keys(domain)
        self.driver.find_element_by_css_selector(
            'button[type="submit"]'
        ).click()

        # Login page
        time.sleep(10)
        self.wait_for_element_by_css_selector(
            'input[name="email"]'
        ).send_keys(username)
        self.wait_for_element_by_css_selector(
            'input[name="password"]'
        ).send_keys(pw)
        self.driver.find_element_by_css_selector(
            'button[type="submit"]'
        ).click()

        # OAuth authorize page
        time.sleep(10)
        self.percy_snapshot('oauth screen - {} {} {}'.format(
            username, pw, url_base_pathname))
        self.wait_for_element_by_css_selector(
            'button[type="submit"]'
        ).click()

    def private_app_authorized(self, url_base_pathname):
        self.solvebio_auth_login_flow(
            self.test_username,
            self.test_password,
            self.test_domain,
            url_base_pathname
        )
        switch_windows(self.driver)
        time.sleep(5)
        self.percy_snapshot('private_app_authorized - {}'.format(
            url_base_pathname))
        try:
            el = self.wait_for_element_by_id('output')
        except:
            print((self.driver.find_element_by_tag_name('body').html))
        self.assertEqual(el.text, 'initial value')

    def test_private_app_authorized_index(self):
        self.private_app_authorized('/')
