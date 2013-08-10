import requests

from .credentials import CredentialsConfig


class SolveClient(object):
    def __init__(self):
        self.auth = CredentialsConfig().get()
        self.session = requests.Session()

    def _request(self):
        pass
