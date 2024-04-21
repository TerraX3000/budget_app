import streamlit as st
import pandas as pd
import glob
from sections import navbar
from functions.utility import (
    get_app_config,
    get_data_file_path,
    get_statement_files,
    get_data_list,
    get_register_dataframe,
    get_dataframe,
    get_new_key,
)
from icecream import ic
import os
import time


def add_statement_to_register(file, account):
    filepath = get_data_file_path("statements")
    uid = account["uid"]
    path = os.path.join(filepath, uid, file.name)
    field_names = []
    standard_field_names = ["Date", "Amount", "Description"]
    fields = {}
    for field_name in standard_field_names:
        fields[field_name] = account[field_name]
    field_names = list(fields.keys())
    reverse_field_map = {value: key for key, value in fields.items()}
    with open(path) as f:
        df = pd.read_csv(f, index_col=None)
        df = df.rename(columns=reverse_field_map)
        df["Date"] = pd.to_datetime(df["Date"])
        df["Category"] = ""
        df["Account"] = account["Account"]
    field_names.extend(["Category", "Account"])
    df = df[field_names]
    df = df.sort_values(["Date"], ascending=[True])
    filepath = get_data_file_path("register")
    path = os.path.join(filepath, uid, file.name)
    df.to_csv(path, index=False, header=True)


def import_statement(file, account):
    add_statement_to_register(file, account)
    imported_files = get_data_list("imported_files")
    imported_files.append(file)
    df = pd.DataFrame.from_dict(imported_files)
    file_path = get_data_file_path("imported_files")
    df.to_csv(file_path, index=False, header=True)


def save_statement(file, account):
    statements_filepath = get_data_file_path("statements")
    uid = account["uid"]
    path = os.path.join(statements_filepath, uid, file.name)
    with open(path, "wb") as f:
        f.write(file.getvalue())


def process_file(key, account, new_key, container):
    file = st.session_state[key]
    save_statement(file, account)
    add_statement_to_register(file, account)
    with container:
        st.success(f"{file.name} saved to {account['Account']}")
    st.session_state["account"] = None
    st.session_state["file_uploader_key"] = new_key


def run():
    st.query_params.page = "import"
    navbar.run()
    st.write("")

    # df = get_dataframe("imported_files")
    # st.dataframe(df, use_container_width=True)
    # imported_files = get_data_list("imported_files")
    # statement_files = get_statement_files()
    if "file_uploader_key" not in st.session_state:
        st.session_state["file_uploader_key"] = f"file-uploader-{get_new_key()}"

    try:
        accounts = get_data_list("accounts")
    except:
        accounts = []
    if not accounts:
        st.warning("Add accounts before importing files.")
    account_dict = {account["Account"]: account for account in accounts}

    file_upload_container = st.container()
    with file_upload_container:
        options = account_dict.keys()
        account = st.selectbox("Account", options=options, index=None, key="account")
        if account:
            statement_files = get_statement_files(account=account)
            if statement_files:
                st.write("Imported Files:")
                imported_files = []
                for file in statement_files:
                    filename = file["filename"].split("/")[-1]
                    imported_files.append(filename)
                imported_files = sorted(imported_files)
                st.dataframe(
                    imported_files,
                    hide_index=None,
                    column_config={"value": st.column_config.Column("Filename")},
                )
            new_key = f"file-uploader-{get_new_key()}"
            file = st.file_uploader(
                "Import Statement",
                key=st.session_state["file_uploader_key"],
                on_change=process_file,
                kwargs={
                    "key": st.session_state["file_uploader_key"],
                    "account": account_dict[account],
                    "new_key": new_key,
                    "container": file_upload_container,
                },
            )
            # if file:
            #     # import_statement(file, account)
            #     # save_file(file, account_dict[account])
            #     st.spinner("Loading...")
            #     time.sleep(3)
            #     file_upload_container.success("File uploaded!")
            #     # st.session_state["file_uploader_key"] = f"file-uploader-{get_new_key()}"

    # for file in statement_files:
    #     if file in imported_files:
    #         continue
    #     else:
    #         col_1, col_2, col_3 = st.columns([1, 2, 1])
    #         with col_1:
    #             st.write(file["account"])
    #         # with col_2:
    #         #     st.write(file["path"])
    #         with col_2:
    #             st.write(file["filename"])
    #         with col_3:
    #             import_file = st.popover("Import")
    #             import_file.checkbox(
    #                 "Import file to register?",
    #                 key=file["filename"],
    #                 on_change=import_statement,
    #                 kwargs={"file": file},
    #             )

    # st.header("Imported Statement Files")
    # st.dataframe(
    #     imported_files, use_container_width=True, height=38 * len(imported_files)
    # )
