# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import solvebio
from ..client import client
from .credentials import get_credentials
from .credentials import save_credentials
from .credentials import delete_credentials


def login_and_save_credentials(*args):
    """
    CLI command to login and persist credentials to a file
    """
    args = args[0]

    solvebio.login(
        api_host=args.api_host,
        api_key=args.api_key,
        access_token=args.access_token,
        # name=args.name,
        # version=args.version,
        debug=args.debug,
    )

    # Print information about the current user
    if not client.is_logged_in():
        print("login: client is not logged in!")

        # Verify if user has provided the wrong credentials file
        if client._host:
            if suggested_host := client.validate_host_is_www_url(client._host):
                print(
                    f"Provided API host is: `{client._host}`. "
                    f"Did you perhaps mean `{suggested_host}`?"
                )
        return

    user = client.whoami()
    print_user(user)

    # fixme: how to detect if login was successful
    save_credentials(
        user["email"].lower(),
        client._auth.token,
        client._auth.token_type,
        solvebio.get_api_host(),
    )
    print("Updated local credentials file.")


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
        print(u'{} (code: {})'.format(e.message, e.status_code))
    else:
        print_user(user)


def print_user(user):
    """
    Prints information about the current user.
    """
    email = user['email']
    domain = user['account']['domain']
    print(f'You are logged-in to the "{domain}" domain as {email}'
          f' (server: {solvebio.get_api_host()}).')
