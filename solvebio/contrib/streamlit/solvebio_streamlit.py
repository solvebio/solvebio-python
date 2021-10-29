import asyncio
import os

import streamlit as st
import solvebio
from dotenv import load_dotenv

from solvebio_auth import SolveBioOAuth2


# Load environment variables from .env file
load_dotenv()


class SolveBioStreamlit:
    """SolveBio OAuth2 wrapper for restricting access to Streamlit apps"""

    # App settings loaded from environment variables or .env file
    SOLVEBIO_CLIENT_ID = os.environ.get("SOLVEBIO_CLIENT_ID", "Application (client) Id")
    SOLVEBIO_SECRET = os.environ.get("SOLVEBIO_SECRET", "Application (client) secret")
    redirect_uri = os.environ.get("REDIRECT_URI", "http://localhost:8501")

    def solvebio_login_component(self, authorization_url):
        """Streamlit component for logging into SolveBio"""

        st.title("Secure Streamlit App")
        st.write(
            f"""
            <h4>
                <a target="_self" href="{authorization_url}">Log in to SolveBio to continue</a>
            </h4>    
            This app requires a SolveBio account. <br>
            <a href="mailto:support@solvebio.com">Contact Support</a>
            """,
            unsafe_allow_html=True,
        )

    def get_token_from_session(self):
        """Reads token from streamlit session state.

        If token is in the session state then the user is authorized to use the app and vice versa.
        """

        if "token" not in st.session_state:
            token = None
        else:
            token = st.session_state["token"]

        return token

    def wrap(self, streamlit_app):
        """SolveBio OAuth2 wrapper around streamlit app"""

        # SolveBio OAuth2 client
        client = SolveBioOAuth2(self.SOLVEBIO_CLIENT_ID, self.SOLVEBIO_SECRET)
        authorization_url = asyncio.run(
            client.get_authorization_url(
                self.redirect_uri,
            )
        )

        # Authorization token from Streamlit session state
        token = self.get_token_from_session()

        if token is None:
            # User is not authrized to use the app
            try:
                # Trying to get the authorization token from the url if successfully authorized
                code = st.experimental_get_query_params()["code"]
            except:
                # Display SolveBio login until user is successfully authorized
                self.solvebio_login_component(authorization_url)
            else:
                try:
                    # Getting the token from token API by sending the authorization code
                    token = asyncio.run(
                        client.get_access_token(code, self.redirect_uri)
                    )
                except:
                    st.error(
                        "This account is not allowed or page was refreshed. Please login again."
                    )
                    self.solvebio_login_component(authorization_url)
                else:
                    # Check if token has expired:
                    if token.is_expired():
                        st.error("Login session has ended. Please login again.")
                        self.solvebio_login_component(authorization_url)
                    else:
                        # User is now authenticated and authorized to use the app
                        # Saving token and solvebio client to the Streamlit session state
                        solvebio_client = solvebio.SolveClient(
                            token=token, token_type="Bearer"
                        )
                        st.session_state.solvebio = solvebio_client
                        st.session_state.token = token
                        streamlit_app()
        else:
            # User is authorized to the the app
            streamlit_app()
