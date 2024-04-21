import streamlit as st
from sections import navbar
from functions.utility import (
    get_dataframe,
    get_data_file_path,
)
from icecream import ic
import os
import uuid
from typing import List


def get_account_fields():
    return {
        "Account Name": "Account",
        "Date Field": "Date",
        "Amount Field": "Amount",
        "Description Field": "Description",
    }


def initialize_accounts():
    filepath = get_data_file_path("accounts")
    is_file = os.path.isfile(filepath)
    fields: List = list(get_account_fields().values())
    fields.insert(0, "uid")
    header = ",".join(fields)
    if not is_file:
        with open(filepath, "w") as f:
            f.write(header)
    st.session_state["initialize_accounts"] = True


def initialize_statements():
    filepath = get_data_file_path("statements")
    is_dir = os.path.isdir(filepath)
    if not is_dir:
        os.mkdir(filepath)
    st.session_state["initialize_statements"] = True


def initialize_register():
    filepath = get_data_file_path("register")
    is_dir = os.path.isdir(filepath)
    if not is_dir:
        os.mkdir(filepath)
    st.session_state["initialize_register"] = True


def all_required_fields():
    fields = get_account_fields().values()
    for field in fields:
        if not st.session_state[field]:
            return False
    return True


def reset_input_fields(fields):
    for field in fields:
        st.session_state[field] = ""


def add_account():
    fields = get_account_fields().values()
    line = ",".join([st.session_state[f"{field}"] for field in fields])
    uid = str(uuid.uuid4())
    accounts_filepath = get_data_file_path("accounts")
    with open(accounts_filepath, "a") as f:
        f.write(f"\n{uid},{line}")
    statements_filepath = get_data_file_path("statements")
    statements_filepath = os.path.join(statements_filepath, uid)
    os.mkdir(statements_filepath)
    register_filepath = get_data_file_path("register")
    register_filepath = os.path.join(register_filepath, uid)
    os.mkdir(register_filepath)
    reset_input_fields(fields)


def run():
    st.query_params.page = "accounts"
    navbar.run()
    if "initialize_accounts" not in st.session_state:
        initialize_accounts()
    if "initialize_statements" not in st.session_state:
        initialize_statements()
    if "initialize_register" not in st.session_state:
        initialize_register()
    accounts_container = st.container()
    form_container = st.container(border=True)

    with form_container:
        st.write("")
        st.header("Add New Account")
        account_fields = get_account_fields()
        columns = st.columns([1] * (len(account_fields) + 1))
        for column, (label, key) in zip(columns, account_fields.items()):
            with column:
                st.text_input(label, key=key)

        is_disabled = not all_required_fields()
        is_add_account = st.button(
            "Add Account",
            disabled=is_disabled,
            on_click=add_account,
            use_container_width=True,
        )

        if is_add_account:
            st.success("Account added!")

    df = get_dataframe("accounts")
    column_order = account_fields.values()
    column_config = {}
    for label, data_field in account_fields.items():
        column_config[data_field] = st.column_config.Column(label)

    with accounts_container:
        st.header("Accounts")
        st.dataframe(
            df,
            column_order=column_order,
            column_config=column_config,
            use_container_width=True,
            hide_index=True,
            height=38 * (len(df) + 1),
        )
