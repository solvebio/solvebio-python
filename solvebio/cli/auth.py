# -*- coding: utf-8 -*-
import getpass

import solvebio
from solvebio.client import client, SolveAPIError
from credentials import get_credentials, delete_credentials, save_credentials


def _ask_for_credentials():
    while True:
        email = raw_input('Email address: ')
        password = getpass.getpass('Password (typing will be hidden): ')
        if email and password:
            return (email, password)
        else:
            print 'Email and password are both required.'


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


def login(args):
    """
    Prompt user for login information (email/password).
    Email and password are used to get the user's auth_token key.
    """
    delete_credentials()

    email, password = _ask_for_credentials()
    data = {
        'email': email,
        'password': password
    }
    try:
        response = client.request('post', '/v1/auth/token', data)
    except SolveAPIError as e:
        print 'Login failed: %s' % e.message
    else:
        save_credentials(email.lower(), response['token'])
        # reset the default client's auth token
        solvebio.api_key = response['token']
        _send_install_report()
        print 'You are now logged-in.'


def logout(args):
    if get_credentials():
        delete_credentials()
        client.auth = None
        print 'You have been logged out.'
    else:
        print 'You are not logged-in.'


def whoami(args):
    creds = get_credentials()
    if creds:
        print creds[0]
        client.get_current_user()
    else:
        print 'You are not logged-in.'
