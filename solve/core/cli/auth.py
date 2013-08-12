#!/usr/bin/python
"""
Copyright (c) 2013 `Solve, Inc. <http://www.solvebio.com>`_.  All rights reserved.
"""
import getpass

from solve.core.client import SolveClient, SolveAPIError
from solve.core.credentials import (get_credentials, delete_credentials,
                                    save_credentials)


def _get_current_user():
    api = SolveClient()
    try:
        return api.get_current_user()
    except SolveAPIError:
        pass
    return None


def _report_install(email, action):
    try:
        api = SolveClient()
        api.post_report(email, action)
    except:
        pass


def ask_for_credentials():
    while True:
        email = raw_input('Email address: ')
        password = getpass.getpass('Password (typing will be hidden): ')
        if email and password:
            return (email, password)
        else:
            print 'Email and password are both required.'


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
    except SolveAPIError:
        pass
    else:
        save_credentials(email.lower(), response['token'])
        try:
            api.post_install_report()
        except Exception:
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
