# -*- coding: utf-8 -*-
import getpass
from urlparse import urlparse

import solvebio
from solvebio.client import client, SolveError
from solvebio.cli.credentials import (get_credentials, delete_credentials,
                                      save_credentials)


last_email = None  # Last email address tried in login()


def _ask_for_credentials(default_email=None):
    while True:
        if default_email and isinstance(default_email, str):
            prompt = 'Email address ({0})'.format(default_email)
        else:
            prompt = 'Email address'

        if solvebio.api_host != 'https://api.solvebio.com':
            prompt += ' for %s' % solvebio.api_host

        email = raw_input(prompt + ': ')
        if email == '':
            email = default_email
        password = getpass.getpass('Password (typing will be hidden): ')
        if email and password:
            return (email, password)
        else:
            print 'Email and password are both required.'
            if default_email is None:
                default_email = email


def _send_install_report():
    import platform
    data = {
        'hostname': platform.node(),
        'python_version': platform.python_version(),
        'python_implementation': platform.python_implementation(),
        'platform': platform.platform(),
        'architecture': platform.machine(),
        'processor': platform.processor(),
        'pyexe_build': platform.architecture()[0]
    }
    try:
        client.request('post', '/v1/reports/install', data)
    except:
        pass


def login(email=None, api_key=None):
    """
    Prompt user for login information (email/password).
    Email and password are used to get the user's auth_token key.
    """
    if api_key is not None:
        old_api_key = solvebio.api_key
        try:
            solvebio.api_key = api_key
            response = client.get('/v1/user', {})
        except SolveError as e:
            print('Login failed: %s' % e.message)
            solvebio.api_key = old_api_key
            return False
        email = response['email']
        save_credentials(email, api_key)
        _send_install_report()
        print('You are now logged-in as %s.' % email)
        return True
    else:
        if email is None:
            global last_email
            email = last_email
        email, password = _ask_for_credentials(email)
        last_email = email
        data = {
            'email': email,
            'password': password}
        try:
            response = client.post('/v1/auth/token', data)
        except SolveError as e:
            print('Login failed: %s' % e.message)
            return False
        else:
            save_credentials(email.lower(), response['token'])
            # reset the default client's auth token
            solvebio.api_key = response['token']
            _send_install_report()
            print('You are now logged-in.')
            return True


def login_if_needed():
    """
    If the credentials file has our api host key use that. Otherwise,
    ask for credentials.
    """

    creds = get_credentials()
    global last_email
    if creds:
        last_email = creds[0]
        msg = "\nYou are logged in as %s" % last_email
        if solvebio.api_host != 'https://api.solvebio.com':
            msg += ' on %s' % solvebio.api_host
        print msg
        return True
    else:
        return login(api_key=solvebio.api_key)

# In the routines below, args is needed because we use a funky
# options-processing routine that requires it.


def opts_login(args):
    """
    Prompt user for login information (email/password).
    Email and password are used to get the user's auth_token key.
    """
    delete_credentials()
    return login()


def opts_logout(args):
    if get_credentials():
        delete_credentials()
        client.auth = None
        print('You have been logged out.')
        return True
    else:
        print('You are not logged-in.')
        return False


def opts_whoami(args):
    creds = get_credentials()
    if creds:
        print creds[0]
    else:
        print 'You are not logged-in.'
