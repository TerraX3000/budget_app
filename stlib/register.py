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


def run():
    st.query_params.page = "register"
    navbar.run()
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
        options = account_dict.keys()
        account = st.selectbox("Account", options=options, index=None)
    with col_2:
        if account:
            files = get_statement_files("register", account=account)
            filenames = {}
            for file in files:
                filename_only = file["filename"].split("/")[-1]
                filenames[file["filename"]] = filename_only

            selected_file = st.selectbox(
                "File",
                options=filenames.keys(),
                format_func=lambda x: filenames.get(x),
                index=None,
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
