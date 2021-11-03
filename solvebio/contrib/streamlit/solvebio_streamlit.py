import asyncio
import os

import streamlit as st
import solvebio

from solvebio_auth import SolveBioOAuth2


class SolveBioStreamlit:
    """SolveBio OAuth2 wrapper for restricting access to Streamlit apps"""

    # App settings loaded from environment variables or .env file
    CLIENT_ID = os.environ.get("CLIENT_ID", "Application (client) Id")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET", "Application (client) secret")
    APP_URL = os.environ.get("APP_URL", "http://localhost:5000")

    def solvebio_login_component(self, authorization_url):
        """Streamlit component for logging into SolveBio"""

        st.title("Secure Streamlit App")
        st.write(
            """
            <h4>
                <a target="_self" href="{}">Log in to SolveBio to continue</a>
            </h4>
            This app requires a SolveBio account. <br>
            <a href="mailto:support@solvebio.com">Contact Support</a>
            """.format(
                authorization_url
            ),
            unsafe_allow_html=True,
        )

    def get_token_from_session(self):
        """Reads token from streamlit session state.

        If token is in the session state then the user is authorized to use the app and vice versa.
        """

        if "token" not in st.session_state:
            token = None
        else:
            token = st.session_state.token

        return token

    def wrap(self, streamlit_app):
        """SolveBio OAuth2 wrapper around streamlit app"""

        # SolveBio OAuth2 client
        oauth_client = SolveBioOAuth2(self.CLIENT_ID, self.CLIENT_SECRET)
        authorization_url = oauth_client.get_authorization_url(
            self.APP_URL,
        )

        # Authorization token from Streamlit session state
        oauth_token = self.get_token_from_session()

        if oauth_token is None:
            # User is not authrized to use the app
            try:
                # Trying to get the authorization token from the url if successfully authorized
                code = st.experimental_get_query_params()["code"]

                # Remove authorization token from the url params
                params = {}
                st.experimental_set_query_params(**params)

            except:
                # Display SolveBio login until user is successfully authorized
                self.solvebio_login_component(authorization_url)
            else:
                try:
                    # Getting the token from token API by sending the authorization code
                    oauth_token = asyncio.run(
                        oauth_client.get_access_token(code, self.APP_URL)
                    )
                except:
                    st.error(
                        "This account is not allowed or page was refreshed. Please login again."
                    )
                    self.solvebio_login_component(authorization_url)
                else:
                    # Check if token has expired:
                    if oauth_token.is_expired():
                        st.error("Login session has ended. Please login again.")
                        self.solvebio_login_component(authorization_url)
                    else:
                        # User is now authenticated and authorized to use the app

                        # SolveClient to acces API
                        solvebio_client = solvebio.SolveClient(
                            token=oauth_token["access_token"],
                            token_type=oauth_token["token_type"],
                        )

                        # Saving token and solvebio client to the Streamlit session state
                        st.session_state.solvebio_client = solvebio_client
                        st.session_state.token = oauth_token

                        streamlit_app()
        else:
            # User is authorized to the the app
            streamlit_app()
