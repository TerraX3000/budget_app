import streamlit as st
from sections import navbar
from icecream import ic


def run():
    query_params = st.query_params.to_dict()
    query_params.pop("page", None)
    st.query_params.clear()
    for key, value in query_params.items():
        st.query_params[key] = value
    navbar.run()
