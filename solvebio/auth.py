from __future__ import absolute_import

import os
from typing import Literal, Tuple

from six.moves.urllib.parse import urlparse

import logging

from requests.auth import AuthBase
import requests

from solvebio import SolveError
from solvebio.cli.credentials import get_credentials, netrc

logger = logging.getLogger("solvebio")


class SolveBioTokenAuth(AuthBase):
    """Custom auth handler for SolveBio API token authentication"""

    def __init__(self, token=None, token_type="Token"):
        self.token = token
        self.token_type = token_type

    def __call__(self, r):
        if self.token:
            r.headers["Authorization"] = "{0} {1}".format(self.token_type, self.token)
        return r

    def __repr__(self):
        if self.token:
            return self.token_type
        else:
            return "Anonymous"


def authenticate(
    host: str,
    token: str,
    token_type: Literal["Bearer", "Token"],
    *,
    raise_on_missing: bool = True,
    debug: bool = False
) -> Tuple[str, SolveBioTokenAuth]:
    """
    Sets login credentials for SolveBio API authentication.

    :param str host: API host url
    :param str token: API access token or API key
    :param str token_type: API token type. `Bearer` is used for access tokens, while `Token` is used for API Keys.
    :param bool raise_on_missing: Raise an exception if no credentials are available.
    """
    # used for debugging
    source_host = None
    source_token = None

    # Find credentials from environment variables
    if not host:
        host = (
            os.environ.get("QUARTZBIO_API_HOST", None) or
            os.environ.get("EDP_API_HOST", None) or
            os.environ.get("SOLVEBIO_API_HOST", None)
        )

    if not token:
        api_key = (
            os.environ.get("QUARTZBIO_API_KEY", None) or
            os.environ.get("EDP_API_KEY", None) or
            os.environ.get("SOLVEBIO_API_KEY", None)
        )

        access_token = (
            os.environ.get("QUARTZ_ACCESS_TOKEN", None) or
            os.environ.get("EDP_ACCESS_TOKEN", None) or
            os.environ.get("SOLVEBIO_ACCESS_TOKEN", None)
        )

        if access_token:
            token = access_token
            token_type = "Bearer"
        elif api_key:
            token = api_key
            token_type = "Token"

        if token:
            source_token = 'envvars'
    else:
        source_token = 'params'

    # Find credentials from local credentials file
    if not token:
        if creds := get_credentials(host):
            token_type = creds.token_type
            token = creds.token

            if host is None:
                # this happens when user/ennvars provided no API host for the login command
                # but the credentials file still contains login credentials
                host = creds.api_host

                if host:
                    source_host = 'creds'
            if token:
                source_token = 'creds'

    if debug:
        # this will tell the user where QB Client found the credentials from
        creds_path = netrc.path()
        print('\n'.join([
            "Login Debug:",
            f"--> Host: {host}\n    (source: {source_host})",
            f"--> Token Type: {token_type}\n    (source: {source_token})",
            "\n1) source: params",
            "   Means that you've passed this through the login CLI command:",
            "   quartzbio login --host <EDP_HOST> --access_token <EDP_TOKEN>",
            "\n   or the quartzbio.login function:",
            "   import quartzbio",
            "   quartzbio.login(debug=True)",
            "\n2) source: creds",
            "   Means that the QB client has saved your credentials in:",
            f"   {creds_path}",
            "\n3) source: envvars",
            "   Means that you've set your credentials through environment variables:",
            "   QUARTZBIO_API_HOST",
            "   QUARTZBIO_ACCESS_TOKEN",
            "   QUARTZBIO_API_KEY",
        ]))

    if not host:
        if raise_on_missing and not debug:
            raise SolveError("No QuartzBio API host is set")
        else:
            return host, None

    host = validate_api_host_url(host)

    # If the domain ends with .solvebio.com, determine if
    # we are being redirected. If so, update the url with the new host
    # and log a warning.
    if host and host.rstrip("/").endswith(".api.solvebio.com"):
        old_host = host.rstrip("/")
        response = requests.head(old_host, allow_redirects=True)
        # Strip the port number from the host for comparison
        new_host = validate_api_host_url(response.url).rstrip("/").replace(":443", "")

        if old_host != new_host:
            logger.warning(
                'API host redirected from "{}" to "{}", '
                "please update your local credentials file".format(old_host, new_host)
            )
            host = new_host

    if token is not None:
        auth = SolveBioTokenAuth(token, token_type)
    else:
        auth = None

    # TODO: warn user if WWW url is provided in edp_login!

    from solvebio import _set_cached_api_host
    _set_cached_api_host(host)

    return host, auth


def validate_api_host_url(url):
    """
    Validate SolveBio API host url.

    Valid urls must not be empty and
    must contain either HTTP or HTTPS scheme.
    """

    # Default to https if no scheme is set
    if "://" not in url:
        url = "https://" + url

    parsed = urlparse(url)
    if parsed.scheme not in ["http", "https"]:
        raise SolveError(
            "Invalid API host: %s. " "Missing url scheme (HTTP or HTTPS)." % url
        )
    elif not parsed.netloc:
        raise SolveError("Invalid API host: %s." % url)

    return parsed.geturl()
