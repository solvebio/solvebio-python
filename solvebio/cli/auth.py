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


def login_and_save_credentials(*args, **kwargs):
    """
    Domain, email and password are used to get the user's API key.
    """
    if args and args[0].api_key:
        # Handle command-line arguments if provided.
        logged_in = solvebio.login(api_key=args[0].api_key,
                                   api_host=solvebio.api_host)
    elif args and args[0].access_token:
        # Handle command-line arguments if provided.
        logged_in = solvebio.login(access_token=args[0].access_token,
                                   api_host=solvebio.api_host)
    elif solvebio.login(**kwargs):
        logged_in = True
    else:
        logged_in = False

    if logged_in:
        # Print information about the current user
        user = client.whoami()
        print_user(user)
        save_credentials(
            user['email'].lower(), client._auth.token,
            client._auth.token_type, solvebio.api_host)
        print('Updated local credentials file.')
    else:
        print('You are not logged-in. Visit '
              'https://docs.solvebio.com/#authentication to get started.')


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
