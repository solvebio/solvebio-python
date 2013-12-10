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


from .solveconfig import solveconfig

from netrc import netrc as _netrc, NetrcParseError
import os

try:
    NETRC_PATH = os.path.join(os.environ['HOME'], ".netrc")
except KeyError:
    raise IOError("Could not find .netrc: $HOME is not set")

# create an empty .netrc (or append in worst case) if it doesn't exist
if not os.path.exists(NETRC_PATH):
    try:
        open(NETRC_PATH, 'a').close()
    except IOError:
        raise Exception("Could not create a netrc file at '%s', permission denied." % NETRC_PATH)


class netrc(_netrc):
    """
    Adds a save() method to netrc
    """

    def save(self, path):
        """Dump the class data in the format of a .netrc file."""
        rep = u""
        for host in self.hosts.keys():
            attrs = self.hosts[host]
            rep = rep + "machine " + host + "\n\tlogin " + unicode(attrs[0]) + "\n"
            if attrs[1]:
                rep = rep + "account " + unicode(attrs[1])
            rep = rep + "\tpassword " + unicode(attrs[2]) + "\n"
        for macro in self.macros.keys():
            rep = rep + "macdef " + macro + "\n"
            for line in self.macros[macro]:
                rep = rep + line
            rep = rep + "\n"

        f = open(path, 'w')
        f.write(rep)
        f.close()


class CredentialsError(BaseException):
    """
    Class to be thrown if the credentials are not found.
    """
    pass


def get_api_key():
    """
    Helper function to get the current user's API key or None.
    """
    try:
        # user can manually override the api_key:
        #   solvebio.api_key = "API_KEY"
        from solvebio import api_key
        return api_key
    except ImportError:
        # otherwise, try to get it from netrc
        creds = get_credentials()
        if creds:
            return creds[1]
        return None


def get_credentials():
    """
    Returns the tuple user / password given a path for the .netrc file.
    Raises CredentialsError if no valid netrc file is found.
    """
    try:
        auths = netrc(NETRC_PATH).authenticators(solveconfig.API_HOST)
    except (IOError, TypeError, NetrcParseError) as e:
        raise CredentialsError(
            'Did not find valid netrc file: ' + str(e))

    if auths:
        return (auths[0], auths[2])
    else:
        return None


def delete_credentials():
    try:
        rc = netrc(NETRC_PATH)
    except (IOError, TypeError, NetrcParseError) as e:
        raise CredentialsError('Could not open netrc file: ' + str(e))

    try:
        del rc.hosts[solveconfig.API_HOST]
    except KeyError:
        pass
    else:
        rc.save(NETRC_PATH)


def save_credentials(email, api_key):
    try:
        rc = netrc(NETRC_PATH)
    except (IOError, TypeError, NetrcParseError) as e:
        raise CredentialsError('Could not open netrc file: ' + str(e))

    # Overwrites any existing credentials
    rc.hosts[solveconfig.API_HOST] = (email, None, api_key)
    rc.save(NETRC_PATH)
