from typing import Any
from typing import Dict
from urllib.parse import urlencode

from httpx_oauth.oauth2 import BaseOAuth2

# SolveBio API OAuth2 endpoints
DEFAULT_SOLVEBIO_URL = "https://my.solvebio.com"
OAUTH2_TOKEN_URL = "https://solvebio.api.solvebio.com/v1/oauth2/token"
OAUTH2_REVOKE_TOKEN_URL = "https://solvebio.api.solvebio.com/v1/oauth2/revoke_token"


class SolveBioOAuth2(BaseOAuth2[Dict[str, Any]]):
    """Class implementing OAuth2 for SolveBio API"""

    def __init__(self, client_id: str, client_secret: str, name: str = "solvebio"):
        super().__init__(
            client_id,
            client_secret,
            DEFAULT_SOLVEBIO_URL,
            OAUTH2_TOKEN_URL,
            revoke_token_endpoint=OAUTH2_REVOKE_TOKEN_URL,
            name=name,
        )

    async def get_authorization_url(self, redirect_uri: str) -> str:
        """Creates authorization url for OAuth2"""

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
        }

        return f"{self.authorize_endpoint}/authorize?{urlencode(params)}"
