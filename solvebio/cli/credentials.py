# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import
from collections import namedtuple
import six

import solvebio

from netrc import netrc as _netrc, NetrcParseError
import os


def as_netrc_machine(api_host):
    return api_host.replace("https://", "").replace("http://", "")


class netrc(_netrc):
    """
    Adds a save() method to netrc
    """

    @staticmethod
    def path():
        if os.name == "nt":
            # Windows
            path = "~\\_solvebio\\credentials"
        else:
            # *nix
            path = "~/.solvebio/credentials"

        try:
            path = os.path.expanduser(path)
        except KeyError:
            # os.path.expanduser can fail when $HOME is undefined and
            # getpwuid fails. See http://bugs.python.org/issue20164
            raise IOError("Could not find any home directory for '{0}'".format(path))

        if not os.path.isdir(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        # create an empty credentials file if it doesn't exist
        if not os.path.exists(path):
            try:
                open(path, "a").close()
            except IOError:
                raise Exception(
                    "Could not create a SolveBio credentials file"
                    " at '%s', permission denied." % path
                )
        return path

    def save(self, path):
        """Dump the class data in the format of a .netrc file."""
        rep = ""
        for host in self.hosts.keys():
            attrs = self.hosts[host]
            rep = (
                rep + "machine " + host + "\n\tlogin " + six.text_type(attrs[0]) + "\n"
            )
            if attrs[1]:
                rep = rep + "\taccount " + six.text_type(attrs[1]) + "\n"
            rep = rep + "\tpassword " + six.text_type(attrs[2]) + "\n"

        f = open(path, "w")
        f.write(rep)
        f.close()


class CredentialsError(BaseException):
    """
    Raised if the credentials are not found.
    """

    pass


ApiCredentials = namedtuple(
    "ApiCredentials", ["api_host", "email", "token_type", "token"]
)


def get_credentials(api_host: str = None) -> ApiCredentials:
    """
    Returns the user's stored API key if a valid credentials file is found.
    Raises CredentialsError if no valid credentials file is found.
    """

    try:
        netrc_obj = netrc(netrc.path())
        if not netrc_obj.hosts:
            return None
    except (IOError, TypeError, NetrcParseError) as e:
        raise CredentialsError("Could not open credentials file: " + str(e))

    netrc_host: str = None

    # if user provides a host, then find its token in the credentials file
    if api_host is not None:
        api_host = api_host.removeprefix("https://")
        if api_host in netrc_obj.hosts:
            netrc_host = api_host
        else:
            # login has failed for the requested host,
            # the rest of the credentials file is ignored
            return None
    else:
        # If there are no stored credentials for the default host,
        # but there are other stored credentials, use the first
        # available option that ends with '.api.quartzbio.com',
        netrc_host = next(
            filter(lambda h: h.endswith(".api.quartzbio.com"), netrc_obj.hosts), None
        )

    # Otherwise use the first available.
    if netrc_host is None:
        netrc_host = next(iter(netrc_obj.hosts))

    if netrc_host is not None:
        return ApiCredentials(
            "https://" + netrc_host, *netrc_obj.authenticators(netrc_host)
        )
    return None


def delete_credentials():
    try:
        netrc_path = netrc.path()
        rc = netrc(netrc_path)
    except (IOError, TypeError, NetrcParseError) as e:
        raise CredentialsError("Could not open netrc file: " + str(e))

    try:
        del rc.hosts[as_netrc_machine(solvebio.get_api_host())]
    except KeyError:
        pass
    else:
        rc.save(netrc_path)


def save_credentials(email, token, token_type="Token", api_host=None):
    api_host = api_host or solvebio.get_api_host()

    try:
        netrc_path = netrc.path()
        rc = netrc(netrc_path)
    except (IOError, TypeError, NetrcParseError) as e:
        raise CredentialsError("Could not open netrc file: " + str(e))

    # Overwrites any existing credentials
    rc.hosts[as_netrc_machine(api_host)] = (email, token_type, token)
    rc.save(netrc_path)
