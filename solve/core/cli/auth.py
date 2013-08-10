#!/usr/bin/python
"""
Copyright (c) 2013 `Solve, Inc. <http://www.solvebio.com>`_.  All rights reserved.
"""
import sys
import getpass

from solve.core.credentials import (get_credentials, delete_credentials,
                               save_credentials)


def verify_credentials():
    # call api get current user with credentials
    # should return a failure message if credentials are invalid
    pass


def signup():
    delete_credentials()
    email = raw_input('Email address: ')

    password, password_2 = 'x', 'y'
    while password != password_2:
        password = getpass.getpass('Password (typing will be hidden): ')
        password_2 = getpass.getpass('Password again: ')
        if password != password_2:
            sys.stderr.write('Passwords don\'t match\n')

    from solve.connection import SolveConnection
    api = SolveConnection()

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
    email = raw_input('Email address: ')
    password = getpass.getpass('Password (typing will be hidden): ')

    from solve.connection import SolveConnection
    api = SolveConnection()

    try:
        response = api.post_login(email, password)
    except Exception as e:
        sys.stderr.write('There was a problem logging you in:\n' + str(e))
    else:
        save_credentials(response['email'], response['auth_token'])


def logout():
    if get_credentials():
        delete_credentials()
        print 'You have been logged out of the Solve client.'
    else:
        print 'You are not logged-in.'
