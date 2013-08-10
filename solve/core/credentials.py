# -*- coding: utf-8 -*-
"""
Manages the credential information (netrc)
"""
from netrc import netrc as _netrc, NetrcParseError
import os

from . import API_HOST
NETRC_PATH = os.path.expanduser('~/.netrc')


class netrc(_netrc):
    """Add a save() method to netrc"""

    def save(self, path=NETRC_PATH):
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


def get_credentials():
    """
    Returns the tuple user / password given a path for the .netrc file.
    Raises CredentialsError if no valid netrc file is found.
    """
    try:
        auths = netrc(NETRC_PATH).authenticators(API_HOST)
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
        del rc.hosts[API_HOST]
    except KeyError:
        pass
    else:
        rc.save()


def save_credentials(email, api_key):
    try:
        rc = netrc(NETRC_PATH)
    except (IOError, TypeError, NetrcParseError) as e:
        raise CredentialsError('Could not open netrc file: ' + str(e))

    # Overwrites any existing credentials
    rc.hosts[API_HOST] = (email, None, api_key)
    rc.save()
