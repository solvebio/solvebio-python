import os
from typing import Any
from typing import Dict
from urllib.parse import urlencode
from urllib.parse import urljoin

import solvebio
from dotenv import load_dotenv

from httpx_oauth.oauth2 import BaseOAuth2


# Load environment variables from .env file
load_dotenv()


class SolveBioOAuth2(BaseOAuth2[Dict[str, Any]]):
    """Class implementing OAuth2 for SolveBio API"""

    # SolveBio API OAuth2 endpoints
    DEFAULT_SOLVEBIO_URL = os.environ.get(
        "DEFAULT_SOLVEBIO_URL", "https://my.solvebio.com"
    )
    OAUTH2_TOKEN_URL = "/v1/oauth2/token"
    OAUTH2_REVOKE_TOKEN_URL = "/v1/oauth2/revoke_token"

    def __init__(self, client_id, client_secret, name="solvebio"):
        super().__init__(
            client_id,
            client_secret,
            self.DEFAULT_SOLVEBIO_URL,
            urljoin(solvebio.api_host, self.OAUTH2_TOKEN_URL),
            revoke_token_endpoint=urljoin(
                solvebio.api_host, self.OAUTH2_REVOKE_TOKEN_URL
            ),
            name=name,
        )

    def get_authorization_url(self, redirect_uri):
        """Creates authorization url for OAuth2"""

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
        }

        return "{}/authorize?{}".format(self.authorize_endpoint, urlencode(params))
