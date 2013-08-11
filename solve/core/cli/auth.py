#!/usr/bin/python
"""
Copyright (c) 2013 `Solve, Inc. <http://www.solvebio.com>`_.  All rights reserved.
"""
import sys
import getpass

from solve.core.client import SolveClient, SolveAPIError
from solve.core.credentials import (get_credentials, delete_credentials,
                                    save_credentials)


def _get_current_user():
    api = SolveClient()
    try:
        return api.get_current_user()
    except SolveAPIError as e:
        # General error message
        print str(e)
    return None


def _report_install(email, action):
    try:
        api = SolveClient()
        api.post_report(email, action)
    except:
        pass


def ask_for_credentials(double_password=False):
    email = raw_input('Email address: ')

    while True:
        password = getpass.getpass('Password (typing will be hidden): ')
        if double_password:
            password_2 = getpass.getpass('Password again: ')
            if password == password_2:
                break
            print 'Passwords don\'t match.'
        else:
            break

    if not email or not password:
        print 'Email and password are both required.'
        sys.exit(1)

    return email, password


def signup():
    delete_credentials()
    email, password = ask_for_credentials(double_password=True)

    api = SolveClient()

    try:
        response = api.post_signup(email, password)
    except SolveAPIError as e:
        print str(e)
    else:
        save_credentials(response['email'], response['auth_token'])
        try:
            api.post_system_report()
        except:
            pass
        print 'Thanks for signing up!'
        # Verify the user's credentials.
        # This will show any account messages as well.
        _get_current_user()


def login():
    """
    Prompt user for login information (email/password).
    Email and password are used to get the user's auth_token key.
    """
    delete_credentials()
    email, password = ask_for_credentials()

    api = SolveClient()

    try:
        response = api.post_login(email, password)
    except SolveAPIError as e:
        print str(e)
    else:
        save_credentials(email.lower(), response['token'])
        try:
            api.post_system_report()
        except:
            pass
        print 'You are now logged-in.'


def logout():
    if get_credentials():
        delete_credentials()
        print 'You have been logged out.'
    else:
        print 'You are not logged-in.'


def whoami():
    creds = get_credentials()
    if creds:
        print creds[0]
        _get_current_user()
    else:
        print 'You are not logged-in.'
