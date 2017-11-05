import os


OAUTH_CLIENT_ID = os.environ.get('SOVEBIO_OAUTH_CLIENT_ID')
OAUTH_TOKEN = os.environ.get('SOVEBIO_OAUTH_TOKEN')
OAUTH_USERNAME = os.environ.get('SOVEBIO_OAUTH_USERNAME')
OAUTH_PASSWORD = os.environ.get('SOVEBIO_OAUTH_PASSWORD')
OAUTH_DOMAIN = os.environ.get('SOLVEBIO_OAUTH_DOMAIN', 'test')

try:
    from .credentials_local import *  # noqa
except:
    pass
