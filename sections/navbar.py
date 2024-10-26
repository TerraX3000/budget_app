import streamlit as st
from icecream import ic
from sections.login import logout


def run():
    query_params = st.query_params.to_dict()
    nav_1, nav_2, nav_3, nav_4, nav_5, nav_6, nav_7, nav_8, spacer, logout_button = st.columns(
        [1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5]
    )
    with nav_1:
        if st.button("Home", use_container_width=True):
            st.query_params.page = "index"
            st.rerun()

    with nav_2:
        if st.button("Register", use_container_width=True):
            st.query_params.page = "register"
            st.rerun()

    with nav_3:
        if st.button("Expenses", use_container_width=True):
            st.query_params.page = "expenses"
            st.rerun()

    with nav_4:
        if st.button("Budget", use_container_width=True):
            st.query_params.page = "budget"
            st.rerun()
    with nav_5:
        if st.button("Monthly Report", use_container_width=True):
            st.query_params.page = "monthly report"
            st.rerun()
    with nav_6:
        if st.button("Import", use_container_width=True):
            st.query_params.page = "import"
            st.rerun()
    with nav_7:
        if st.button("Accounts", use_container_width=True):
            st.query_params.page = "accounts"
            st.rerun()
    with nav_8:
        if st.button("Analysis", use_container_width=True):
            st.query_params.page = "analysis"
            st.rerun()
    with logout_button:
        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()
