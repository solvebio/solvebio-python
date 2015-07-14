from __future__ import absolute_import
from django.conf import settings
import solvebio

API_HOST = getattr(settings, 'SOLVEBIO_API_HOST', None)
API_KEY = getattr(settings, 'SOLVEBIO_API_KEY', None)
DATASET_ALIASES = getattr(settings, 'SOLVEBIO_DATASET_ALIASES', {})
# Application OAuth2 credentials
APP_ID = getattr(settings, 'SOLVEBIO_APP_ID', None)
APP_SECRET = getattr(settings, 'SOLVEBIO_APP_SECRET', None)
# Default access token settings
ACCESS_TOKEN = {
    'CACHE_KEY': 'solvebio:access_token',
    'CACHE_TIMEOUT': 80000,
    'SCOPE': 'read'
}
ACCESS_TOKEN.update(getattr(settings, 'SOLVEBIO_ACCESS_TOKEN', {}) or {})

if API_HOST:
    solvebio.api_host = API_HOST

if API_KEY:
    solvebio.api_key = API_KEY
else:
    # attempt to get API key from get_credentials (local .netrc)
    from solvebio.credentials import get_credentials

    try:
        solvebio.api_key = API_KEY = get_credentials()[1]
    except:
        pass
