# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from six.moves import input as raw_input

import getpass

import solvebio
from ..client import client, SolveError
from .credentials import get_credentials
from .credentials import save_credentials
from .credentials import delete_credentials


def _ask_for_credentials():
    """
    Asks the user for their email and password.
    """
    print('Please enter your SolveBio credentials')
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
        print(
            'Your domain uses Single Sign-On (SSO). '
            'Please visit https://{}.solvebio.com/settings/security '
            'for instructions on how to log in.'.format(domain))
        return None


def login_and_save(*args, **kwargs):
    """
    Attempt to "log the user in" with provided credentials.
    Update local credentials if successful.
    """
    user = login(*args, **kwargs)
    if user:
        save_credentials(
            solvebio.api_host, user['email'].lower(),
            client._auth.token_type, client._auth.token)
        print('Updated local credentials file.')


def login(*args, **kwargs):
    """
    Prompt user for login information (domain/email/password).
    Domain, email and password are used to get the user's API key.
    """

    if args and args[0].api_key:
        # Handle command-line arguments if provided.
        logged_in = solvebio.login(api_key=args[0].api_key)
    elif args and args[0].access_token:
        # Handle command-line arguments if provided.
        logged_in = solvebio.login(access_token=args[0].access_token)
    elif solvebio.login(**kwargs):
        logged_in = True
    else:
        logged_in = interactive_login()

    if logged_in:
        # Print information about the current user
        user = client.whoami()
        print_user(user)
        return user
    else:
        print('Not logged-in. Requests to SolveBio will fail.')


def interactive_login():
    """
    Force an interactive login via the command line.
    Sets the global API key and updates the client auth.
    """
    solvebio.access_token = None
    solvebio.api_key = None
    client.set_token()

    creds = _ask_for_credentials()
    if not creds:
        return False
    elif not all(creds):
        print("Domain, email, and password are all required.")
        return False

    try:
        domain, email, password = creds
        response = client.post('/v1/auth/token', {
            'domain': domain.replace('.solvebio.com', ''),
            'email': email,
            'password': password
        })
    except SolveError as e:
        print('Login failed: {0}'.format(e))
        return False
    else:
        solvebio.api_key = response['token']
        client.set_token()
        return True


def logout(*args):
    """
    Delete's the user's locally-stored credentials.
    """
    if get_credentials():
        delete_credentials()
        print('You have been logged out.')
    else:
        print('You are not logged-in.')


def whoami(*args, **kwargs):
    """
    Prints information about the current user.
    Assumes the user is already logged-in.
    """
    try:
        user = client.whoami()
    except Exception as e:
        print(e.message)
    else:
        print_user(user)


def print_user(user):
    """
    Prints information about the current user.
    """
    email = user['email']
    domain = user['account']['domain']
    print('You are logged-in to the "{}" domain as {} (server: {}).'
          .format(domain, email, solvebio.api_host))
