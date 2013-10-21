# -*- coding: utf-8 -*-
#
# Copyright © 2013 Solve, Inc. <http://www.solvebio.com>. All rights reserved.
#
# email: contact@solvebio.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
        # reset the default client's auth token
        client.auth = None

        try:
            client.post_install_report()
        except Exception:
            pass

        print 'You are now logged-in.'
    else:
        print 'Login failed.'


def logout(args):
    if get_credentials():
        delete_credentials()
        client.auth = None
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
