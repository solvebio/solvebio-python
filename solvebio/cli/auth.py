# -*- coding: utf-8 -*-
import getpass

import solvebio
from solvebio.client import client, SolveError
from solvebio.credentials import (get_credentials, delete_credentials,
                                  save_credentials)


def _ask_for_credentials(default_email=None):
    while True:
        if default_email:
            prompt = 'Email address ({0}): '.format(default_email)
        else:
            prompt = 'Email address: '

        email = raw_input(prompt)
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


def login(args):
    """
    Prompt user for login information (email/password).
    Email and password are used to get the user's auth_token key.
    """
    delete_credentials()

    email, password = _ask_for_credentials(args)
    data = {
        'email': email,
        'password': password
    }
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


def logout(args):
    if get_credentials():
        delete_credentials()
        client.auth = None
        print('You have been logged out.')
    else:
        print('You are not logged-in.')


def whoami(args):
    creds = get_credentials()
    if creds:
        print creds[0]
    else:
        print 'You are not logged-in.'
