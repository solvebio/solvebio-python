import streamlit as st
import pandas as pd

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from solvebio_streamlit import SolveBioStreamlit
# from solvebio.contrib.streamlit.solvebio_streamlit import SolveBioStreamlit


@st.cache
def get_personal_vault_items(vault):
    """Getting items from personal vaulet (caching using Streamlit cache mechanism)"""

    files = vault.files()
    folders = vault.folders()
    datasets = vault.datasets()

    return files, folders, datasets


def streamlit_demo_app():
    """Streamlit demo app

    It fetches the SolveClient (initialised with OAuth2 token) from Streamlit session state
    and makes API call through that client.
    """

    # Getting the sovle client from the Streamlit session state
    solvebio_client = st.session_state.solvebio_client

    st.title("Solvebio app")

    # SolveBio user
    user = solvebio_client.User.retrieve()
    st.header("{}'s personal vault overview:".format(user["first_name"]))

    # Personal vault
    vault = solvebio_client.Vault.get_personal_vault()
    st.write(vault["description"])

    files, folders, datasets = get_personal_vault_items(vault)

    # Visualising the stats from personal vault
    data = {
        "Number of files": [files["total"]],
        "Number of datasets": [datasets["total"]],
        "Number of folders": [folders["total"]],
    }
    chart_data = pd.DataFrame.from_dict(
        data, columns=["Number of items"], orient="index"
    )
    st.write(chart_data)
    st.bar_chart(chart_data)

    # Listing items from personal vault
    st.subheader("List selected items")
    option = st.radio("Select SolveBio platform:", ("Files", "Folders", "Datasets"))
    if option == "Files":
        for item in files:
            st.markdown("- {}".format(item["filename"]))
    elif option == "Folders":
        for item in folders:
            st.markdown("- {}".format(item["filename"]))
    elif option == "Datasets":
        for item in datasets:
            st.markdown("- {}".format(item["filename"]))


# Wrapping Streamlit app with SolveBio OAuth2
secure_app = SolveBioStreamlit()
secure_app.wrap(streamlit_app=streamlit_demo_app)
