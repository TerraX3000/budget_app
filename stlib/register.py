import streamlit as st
import pandas as pd
import glob
from sections import navbar
from functions.utility import (
    get_register_dataframe,
    get_budget_categories,
    add_update_delete_register,
    get_app_config,
    get_statement_files,
    get_dataframe,
    get_data_list,
)
import datetime
from icecream import ic
from typing import List


def set_state(key, options: List):
    index = options.index(st.session_state[key])
    st.session_state["register"][key] = index
    if key == "account":
        st.session_state["register"]["file"] = 0


def run():
    st.query_params.page = "register"
    navbar.run()
    if "register" not in st.session_state:
        st.session_state["register"] = {}
        st.session_state["register"]["account"] = 0
        st.session_state["register"]["file"] = 0
    col_1, col_2, spacer = st.columns([2, 2, 1])
    selected_file = None

    try:
        accounts = get_data_list("accounts")
    except:
        accounts = []
    if not accounts:
        st.warning("Add accounts before importing files.")
    account_dict = {account["Account"]: account for account in accounts}

    with col_1:
        options = list(account_dict.keys())
        options.insert(0, "")
        account = st.selectbox(
            "Account",
            options=options,
            index=st.session_state["register"]["account"],
            key="account",
            on_change=set_state,
            kwargs={"key": "account", "options": options},
        )
    with col_2:
        if account:
            files = get_statement_files("register", account=account)
            filenames = {}
            for file in files:
                filename_only = file["filename"].split("/")[-1]
                filenames[file["filename"]] = filename_only
            options = sorted(list(filenames.keys()))
            options.insert(0, "")
            selected_file = st.selectbox(
                "File",
                options=options,
                format_func=lambda x: filenames.get(x, ""),
                index=st.session_state["register"]["file"],
                key="file",
                on_change=set_state,
                kwargs={"key": "file", "options": options},
            )

    if selected_file:
        df = get_register_dataframe(filename=selected_file)
        df = df.sort_values(["Date", "Account"], ascending=[True, True])
        with st.container():
            categories = get_budget_categories()
            key = "register"
            column_order = list(df.columns)
            column_order.remove("Account")
            st.data_editor(
                df,
                use_container_width=True,
                key=key,
                height=38 * len(df),
                on_change=add_update_delete_register,
                kwargs={"df": df, "data_key": key, "filename": selected_file},
                hide_index=True,
                num_rows="fixed",
                column_order=column_order,
                column_config={
                    "Category": st.column_config.SelectboxColumn(
                        "Category",
                        help="Budget category for this item",
                        options=categories,
                    ),
                    "Amount": st.column_config.NumberColumn(
                        "Amount",
                        format="%.2f",
                    ),
                    "Date": st.column_config.DateColumn(
                        "Date",
                        format="MMMM D, YYYY",
                    ),
                },
            )

    st.json(st.session_state)
