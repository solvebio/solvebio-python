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
        sys.stdout.write(str(e) + '\n')
    return None


def ask_for_credentials(double_password=False):
    email = raw_input('Email address: ')

    while True:
        password = getpass.getpass('Password (typing will be hidden): ')
        if double_password:
            password_2 = getpass.getpass('Password again: ')
            if password == password_2:
                break
            sys.stdout.write('Passwords don\'t match.\n')
        else:
            break

    if not email or not password:
        sys.stdout.write('Email and password are both required.\n')
        sys.exit(1)

    return email, password


def signup():
    delete_credentials()
    email, password = ask_for_credentials(double_password=True)

    api = SolveClient()

    try:
        response = api.post_signup(email, password)
    except SolveAPIError as e:
        sys.stdout.write('There was a problem signing you up:\n' + str(e) + '\n')
    else:
        save_credentials(response['email'], response['auth_token'])
        _get_current_user()


def login():
    """Prompt user for login information (email/password).
    Email and password are used to get the user's auth_token key.
    """
    delete_credentials()
    email, password = ask_for_credentials()

    api = SolveClient()

    try:
        response = api.post_login(email, password)
    except SolveAPIError as e:
        sys.stdout.write('There was a problem logging you in:\n' + str(e) + '\n')
    else:
        save_credentials(email.lower(), response['token'])
        sys.stdout.write('You are now logged-in.\n')


def logout():
    if get_credentials():
        delete_credentials()
        sys.stdout.write('You have been logged out of the Solve client.\n')
    else:
        sys.stdout.write('You are not logged-in.\n')


def whoami():
    if get_credentials():
        response = _get_current_user()
        if response:
            sys.stdout.write('Logged-in as: %s\n' % response['email'])
    else:
        sys.stdout.write('You are not logged-in.\n')
