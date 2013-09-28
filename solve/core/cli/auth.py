#!/usr/bin/python
"""
Copyright (c) 2013 `Solve, Inc. <http://www.solvebio.com>`_.  All rights reserved.
"""
import getpass

from ..client import client
from ..credentials import get_credentials, delete_credentials, save_credentials


def _ask_for_credentials():
    while True:
        email = raw_input('Email address: ')
        password = getpass.getpass('Password (typing will be hidden): ')
        if email and password:
            return (email, password)
        else:
            print 'Email and password are both required.'


def login(args):
    """
    Prompt user for login information (email/password).
    Email and password are used to get the user's auth_token key.
    """
    delete_credentials()
    email, password = _ask_for_credentials()

    response = client.post_login(email, password)

    if response:
        save_credentials(email.lower(), response['token'])
        client.reset_auth(token=response['token'])

        try:
            client.post_install_report()
        except Exception:
            pass
        print 'Loading datasets...'
        from ..dataset import root
        root.refresh()
        print 'You are now logged-in.'
    else:
        print 'Login failed.'


def logout(args):
    if get_credentials():
        delete_credentials()
        client.reset_auth()
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
