# -*- coding: utf-8 -*-
import getpass

import solvebio
from solvebio.client import client, SolveError
from solvebio.cli.credentials import (get_credentials, delete_credentials,
                                      save_credentials)


def _print_msg(msg):
    if solvebio.api_host != 'https://api.solvebio.com':
        msg += ' ({0})'.format(solvebio.api_host)
    print(msg + '.')


def _ask_for_credentials():
    """
    Asks the user for their email and password.
    """
    _print_msg('Enter your SolveBio credentials')
    email = raw_input('Email: ')
    password = getpass.getpass('Password (typing will be hidden): ')
    return (email, password)


def _send_install_report():
    import platform
    data = {
        'client': 'python',
        'client_version': solvebio.version.VERSION,
        'python_version': platform.python_version(),
        'python_implementation': platform.python_implementation(),
        'platform': platform.platform(),
        'architecture': platform.machine(),
        'processor': platform.processor(),
        'pyexe_build': platform.architecture()[0]
    }
    try:
        client.request('post', '/v1/reports/install', data=data)
    except:
        pass


def login(*args):
    """
    Prompt user for login information (email/password).
    Email and password are used to get the user's API key.
    """
    email, password = _ask_for_credentials()

    if not email or not password:
        print("Email and password are both required.")
        return False

    try:
        response = client.post('/v1/auth/token', {
            'email': email,
            'password': password
        })
    except SolveError as e:
        print('Login failed: {0}'.format(e))
        return False

    delete_credentials()
    save_credentials(email.lower(), response['token'])
    solvebio.api_key = response['token']
    _send_install_report()
    _print_msg('You are now logged-in as {0}'.format(email))
    return True


def logout(*args):
    """
    Delete's the user's locally-stored credentials.
    """
    if get_credentials():
        delete_credentials()
        _print_msg('You have been logged out')
        return True

    _print_msg('You are not logged-in')
    return False


def whoami(*args):
    """
    Retrieves the email for the logged-in user.
    Uses local credentials or api_key if found.
    """
    email, api_key = None, solvebio.api_key

    # Existing api_key overrides local credentials file
    if solvebio.api_key:
        try:
            user = client.get('/v1/user', {})
            email = user['email']
        except SolveError as e:
            solvebio.api_key = api_key = None
            _print_msg("Error: {0}".format(e))
    else:
        try:
            email, api_key = get_credentials()
        except:
            pass

    if email:
        _print_msg('You are logged in as {0}'.format(email))
    else:
        _print_msg('You are not logged-in')

    return email, api_key
