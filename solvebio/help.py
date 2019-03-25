from __future__ import absolute_import
from __future__ import print_function

from six.moves.urllib.parse import urljoin

try:
    import webbrowser
except ImportError:
    webbrowser = None


def open_help(path):
    url = urljoin('https://www.solvebio.com/', path)
    try:
        webbrowser.open(url)
    except webbrowser.Error:
        print('The SolveBio Python client was unable to open the following '
              'URL: %s' % url)
