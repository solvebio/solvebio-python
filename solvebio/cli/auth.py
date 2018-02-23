# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from six.moves import input as raw_input

import getpass

import solvebio
from ..client import client, SolveError
from .credentials import (
    get_credentials,
    delete_credentials,
    save_credentials
)


def _print_msg(msg):
    if solvebio.api_host != 'https://api.solvebio.com':
        msg += ' ({0})'.format(solvebio.api_host)
    print(msg + '.')


def _ask_for_credentials():
    """
    Asks the user for their email and password.
    """
    _print_msg('Please enter your SolveBio credentials')
    domain = raw_input('Domain (e.g. <domain>.solvebio.com): ')
    email = raw_input('Email: ')
    password = getpass.getpass('Password (typing will be hidden): ')
    return (domain, email, password)


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
    Prompt user for login information (domain/email/password).
    Domain, email and password are used to get the user's API key.
    """
    domain, email, password = _ask_for_credentials()

    if not all([domain, email, password]):
        print("Domain, email, and password are all required.")
        return False

    try:
        response = client.post('/v1/auth/token', {
            'domain': domain.replace('.solvebio.com', ''),
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
    api_key = solvebio.api_key
    domain, email, role = None, None, None

    # Existing api_key overrides local credentials file
    if not solvebio.api_key:
        try:
            email, api_key = get_credentials()
            solvebio.api_key = api_key
        except:
            pass

    try:
        user = client.get('/v1/user', {})
        email = user['email']
        domain = user['account']['domain']
        role = user['role']
    except SolveError as e:
        solvebio.api_key = None
        api_key = None
        _print_msg("Error: {0}".format(e))

    if email:
        _print_msg('You are logged-in to the "{0}" domain '
                   'as {1} with role {2}'
                   .format(domain, email, role))
    else:
        _print_msg('You are not logged-in')

    return email, api_key
