# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from six.moves import input as raw_input

import sys
import getpass

import solvebio
from ..client import client, SolveError
from .credentials import get_credentials
from .credentials import save_credentials
from .credentials import delete_credentials


def _print_msg(msg):
    if solvebio.api_host != 'https://api.solvebio.com':
        msg += ' ({0})'.format(solvebio.api_host)
    print(msg)


def _ask_for_credentials():
    """
    Asks the user for their email and password.
    """
    _print_msg('Please enter your SolveBio credentials')
    domain = raw_input('Domain (e.g. <domain>.solvebio.com): ')
    # Check to see if this domain supports password authentication
    try:
        account = client.request('get', '/p/accounts/{}'.format(domain))
        auth = account['authentication']
    except:
        raise SolveError('Invalid domain: {}'.format(domain))

    # Account must support password-based login
    if auth.get('login') or auth.get('SAML', {}).get('simple_login'):
        email = raw_input('Email: ')
        password = getpass.getpass('Password (typing will be hidden): ')
        return (domain, email, password)
    else:
        _print_msg(
            'Your domain uses Single Sign-On (SSO). '
            'Please visit https://{}.solvebio.com/settings/security '
            'for instructions on how to log in.'.format(domain))
        sys.exit(1)


def login(*args, **kwargs):
    """
    Prompt user for login information (domain/email/password).
    Domain, email and password are used to get the user's API key.

    Always updates the stored credentials file.
    """
    if args and args[0].api_key:
        # Handle command-line arguments if provided.
        solvebio.login(api_key=args[0].api_key)
    elif kwargs:
        # Run the global login() if kwargs are provided
        # or local credentials are found.
        solvebio.login(**kwargs)
    else:
        interactive_login()

    # Print information about the current user
    user = client.whoami()

    if user:
        print_user(user)
        save_credentials(user['email'].lower(), solvebio.api_key)
        _print_msg('Updated local credentials.')
        return True
    else:
        _print_msg('Invalid credentials. You may not be logged-in.')
        return False


def interactive_login():
    """
    Force an interactive login via the command line.
    Sets the global API key and updates the client auth.
    """
    solvebio.access_token = None
    solvebio.api_key = None
    client.set_token()

    domain, email, password = _ask_for_credentials()
    if not all([domain, email, password]):
        print("Domain, email, and password are all required.")
        return

    try:
        response = client.post('/v1/auth/token', {
            'domain': domain.replace('.solvebio.com', ''),
            'email': email,
            'password': password
        })
    except SolveError as e:
        print('Login failed: {0}'.format(e))
    else:
        solvebio.api_key = response['token']
        client.set_token()


def logout(*args):
    """
    Delete's the user's locally-stored credentials.
    """
    if get_credentials():
        delete_credentials()
        _print_msg('You have been logged out.')

    _print_msg('You are not logged-in.')


def whoami(*args, **kwargs):
    """
    Prints information about the current user.
    Assumes the user is already logged-in.
    """
    user = client.whoami()

    if user:
        print_user(user)
    else:
        print('You are not logged-in.')


def print_user(user):
    """
    Prints information about the current user.
    """
    email = user['email']
    domain = user['account']['domain']
    role = user['role']
    print('You are logged-in to the "{0}" domain '
          'as {1} with role {2}.'
          .format(domain, email, role))
