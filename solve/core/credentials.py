# -*- coding: utf-8 -*-
"""
Manages the credential information (netrc)
"""
from .solveconfig import solveconfig

from netrc import netrc as _netrc, NetrcParseError
import os


class netrc(_netrc):
    """Add a save() method to netrc"""

    def __init__(self, file=None):
        self.file = file
        if self.file is None:
            try:
                self.file = os.path.join(os.environ['HOME'], ".netrc")
            except KeyError:
                raise IOError("Could not find .netrc: $HOME is not set")

        self.hosts = {}
        self.macros = {}

        if os.path.exists(self.file):
            fp = open(self.file)
        else:
            # file doesnt exist yet
            fp = open(self.file, 'w+')

        self._parse(self.file, fp)

    def save(self):
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

        f = open(self.file, 'w')
        f.write(rep)
        f.close()


class CredentialsError(BaseException):
    """
    Class to be thrown if the credentials are not found.
    """
    pass


def get_api_key():
    """Helper function to get the current user's API key or None."""
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
        auths = netrc().authenticators(solveconfig.API_HOST)
    except (IOError, TypeError, NetrcParseError) as e:
        raise CredentialsError(
            'Did not find valid netrc file: ' + str(e))

    if auths:
        return (auths[0], auths[2])
    else:
        return None


def delete_credentials():
    try:
        rc = netrc()
    except (IOError, TypeError, NetrcParseError) as e:
        raise CredentialsError('Could not open netrc file: ' + str(e))

    try:
        del rc.hosts[solveconfig.API_HOST]
    except KeyError:
        pass
    else:
        rc.save()


def save_credentials(email, api_key):
    try:
        rc = netrc()
    except (IOError, TypeError, NetrcParseError) as e:
        raise CredentialsError('Could not open netrc file: ' + str(e))

    # Overwrites any existing credentials
    rc.hosts[solveconfig.API_HOST] = (email, None, api_key)
    rc.save()
