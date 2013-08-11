#!/usr/bin/python
"""
Copyright (c) 2013 `Solve, Inc. <http://www.solvebio.com>`_.  All rights reserved.
"""
import sys
import getpass

from solve.core.client import SolveClient
from solve.core.credentials import (get_credentials, delete_credentials,
                                    save_credentials)


def verify_credentials():
    # call api get current user with credentials
    # should return a failure message if credentials are invalid
    pass


def ask_for_credentials(double_password=False):
    email = raw_input('Email address: ')

    while True:
        password = getpass.getpass('Password (typing will be hidden): ')
        if double_password:
            password_2 = getpass.getpass('Password again: ')
            if password == password_2:
                break
            sys.stderr.write('Passwords don\'t match\n')
        else:
            break

    return email, password


def signup():
    delete_credentials()
    email, password = ask_for_credentials(double_password=True)

    api = SolveClient()

    try:
        response = api.post_signup(email, password)
    except Exception as e:
        sys.stderr.write('There was a problem signing you up:\n' + str(e))
    else:
        save_credentials(response['email'], response['auth_token'])
        verify_credentials()


def login():
    """Prompt user for login information (email/password).
    Email and password are used to get the user's auth_token key.
    """
    delete_credentials()
    email, password = ask_for_credentials()

    api = SolveClient()

    try:
        response = api.post_login(email, password)
    except Exception as e:
        sys.stderr.write('There was a problem logging you in:\n' + str(e))
    else:
        print response
        # save_credentials(response['email'], response['auth_token'])


def logout():
    if get_credentials():
        delete_credentials()
        print 'You have been logged out of the Solve client.'
    else:
        print 'You are not logged-in.'


def whoami():
    if get_credentials():
        api = SolveClient()
        api.get_current_user()
    else:
        print 'You are not logged-in'
