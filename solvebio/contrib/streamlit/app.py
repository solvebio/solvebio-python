import streamlit as st
from solvebio_streamlit import SolveBioStreamlit


def streamlit_demo_app():
    st.title("Solvebio app")
    option = st.radio("Select SolveBio platform:", ("Hive", "Mesh", "Core"))

    if option == "Hive":
        st.write(
            "HIVE is an on-demand network of individually-vetted genomics specialists."
        )
    elif option == "Mesh":
        st.write("MESH is a dynamic, web-based interface for genomics information.")
    elif option == "Core":
        st.write("CORE is a system of technologies for managing genomic data at scale.")


# Wrapping Streamlit app with SolveBio OAuth2
secure_app = SolveBioStreamlit()
secure_app.wrap(streamlit_app=streamlit_demo_app)
