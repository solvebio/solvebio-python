import os

from solvebio.cli.credentials import get_credentials


class EDPClientCredentialsProvider:

    def __init__(self):
        """
        Credentials are discovered in the following priority:
        1) Direct parameters (when using solvebio.SolveClient() or solvebio.login() from the SDK)

            This way is naturally NOT supported for the following setups:
            - Solvebio python entry point (solvebio as a global command)
            - Running solvebio as package (__main__.py)
            - Solvebio unit tests
        2) Environment variables
            - SOLVEBIO_API_HOST
            - SOLVEBIO_ACCESS_TOKEN
            - SOLVEBIO_API_KEY
        3) System credentials file - can be found in:
            - Nix:      ~/.solvebio/credentials
            - Windows:  %USERPROFILE%/_solvebio/credentials

        EDP Supports access tokens and api keys, albeit api keys are deprecated
        and discouraged to use in the future.
        """

        # @todo: @important: Currently this flow is only supported for Unit Tests
        #                    see login() and get_credentials()
        #                    in the future this should be the single source of truth
        #                    for finding creds across all public entries

        # @todo: perhaps passing by parameters can be mitigated to this class as well
        self.api_host: str = None
        self.api_key: str = None
        self.access_token: str = None
        self.token_type: str = None
        self.credentials_source: str = None

        self.get_credentials()

    @property
    def as_dict(self):
        """
        Adapter for solvebio.SolveClient
        """
        return {
            "host": self.api_host,
            "token": self.access_token if (self.token_type == 'Bearer' or not self.token_type)  else self.api_key,
            "token_type": self.token_type
        }

    def get_credentials(self):
        # option 2: find by environment variables
        self.access_token = os.environ.get("SOLVEBIO_ACCESS_TOKEN")
        self.api_key = os.environ.get('SOLVEBIO_API_KEY')
        self.api_host = os.environ.get('SOLVEBIO_API_HOST')

        if self.api_host and (self.api_token or self.api_key):
            self.credentials_source = 'environment_variables'

            if self.access_token:
                self.token_type = 'Bearer'
            elif self.api_key:
                self.token_type = 'Token'
            return

        # option 3: find by netrc file
        creds = get_credentials()
        if creds:
            self.api_host, _, self.token_type, _token_or_key = creds

            self.credentials_source = 'netrc_file'

            if 'Bearer' == self.token_type:
                self.access_token = _token_or_key
                self.api_key = None
            else:
                self.api_key = _token_or_key
                self.access_token = None
            return
