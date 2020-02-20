from __future__ import absolute_import

from six.moves.urllib.parse import urlparse

from ..errors import SolveError


def validate_api_host_url(url):
    """
    Validate SolveBio API host url.

    Valid urls must not be empty and
    must contain either HTTP or HTTPS scheme.
    """
    if not url:
        raise SolveError('No SolveBio API host is set')

    # Default to https if no scheme is set
    if '://' not in url:
        url = 'https://' + url

    parsed = urlparse(url)
    if parsed.scheme not in ['http', 'https']:
        raise SolveError(
            'Invalid API host: %s. '
            'Missing url scheme (HTTP or HTTPS).' % url
        )
    elif not parsed.netloc:
        raise SolveError('Invalid API host: %s.' % url)

    return parsed.geturl()
