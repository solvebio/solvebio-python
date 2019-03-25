# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import
import six

import solvebio

from netrc import netrc as _netrc, NetrcParseError
import os

from six.moves.urllib.parse import urlparse


class netrc(_netrc):
    """
    Adds a save() method to netrc
    """
    @staticmethod
    def path():
        if os.name == 'nt':
            # Windows
            path = '~\\_solvebio\\credentials'
        else:
            # *nix
            path = '~/.solvebio/credentials'

        try:
            path = os.path.expanduser(path)
        except KeyError:
            # os.path.expanduser can fail when $HOME is undefined and
            # getpwuid fails. See http://bugs.python.org/issue20164
            raise IOError(
                "Could not find any home directory for '{0}'"
                .format(path))

        if not os.path.isdir(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        # create an empty credentials file if it doesn't exist
        if not os.path.exists(path):
            try:
                open(path, 'a').close()
            except IOError:
                raise Exception("Could not create a SolveBio credentials file"
                                " at '%s', permission denied." % path)
        return path

    def save(self, path):
        """Dump the class data in the format of a .netrc file."""
        rep = ""
        for host in self.hosts.keys():
            attrs = self.hosts[host]
            rep = rep + "machine " + host + "\n\tlogin " \
                + six.text_type(attrs[0]) + "\n"
            if attrs[1]:
                rep = rep + "account " + six.text_type(attrs[1])
            rep = rep + "\tpassword " + six.text_type(attrs[2]) + "\n"
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
    Raised if the credentials are not found.
    """
    pass


def get_credentials():
    """
    Returns the user's stored API key if a valid credentials file is found.
    Raises CredentialsError if no valid credentials file is found.
    """
    try:
        netrc_path = netrc.path()
        auths = netrc(netrc_path).authenticators(
            urlparse(solvebio.api_host).netloc)
    except (IOError, TypeError, NetrcParseError) as e:
        raise CredentialsError(
            'Could not open credentials file: ' + str(e))

    if auths:
        # auths = (login, account, password)
        return auths[2]
    else:
        return None


def delete_credentials():
    try:
        netrc_path = netrc.path()
        rc = netrc(netrc_path)
    except (IOError, TypeError, NetrcParseError) as e:
        raise CredentialsError('Could not open netrc file: ' + str(e))

    try:
        del rc.hosts[urlparse(solvebio.api_host).netloc]
    except KeyError:
        pass
    else:
        rc.save(netrc_path)


def save_credentials(email, api_key):
    try:
        netrc_path = netrc.path()
        rc = netrc(netrc_path)
    except (IOError, TypeError, NetrcParseError) as e:
        raise CredentialsError('Could not open netrc file: ' + str(e))

    # Overwrites any existing credentials
    rc.hosts[urlparse(solvebio.api_host).netloc] = (email, None, api_key)
    rc.save(netrc_path)
