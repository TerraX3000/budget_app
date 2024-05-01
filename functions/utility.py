import streamlit as st
import pandas as pd
from typing import Tuple, Dict, List, Union
from icecream import ic
import yaml
import json
import random
import string
import glob
import os
import csv


def read_yaml(file_path) -> Union[Dict, List]:
    """Read the specified file and return as a dictionary or list."""
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


def get_new_key(k=6):
    key = "".join(random.choices(string.ascii_lowercase + string.digits, k=k))
    return key


def get_app_config(config_name=None):
    path = "config_stlib.yaml"
    app_config = read_yaml(path)
    if config_name:
        return app_config[config_name]
    return app_config


def get_data_file_path(file_type):
    file_path = get_app_config("data_files")[file_type]
    data_file_path = f"data_files/{file_path}"
    return data_file_path


def get_statement_files(type="statements", account=None):
    filepath = get_data_file_path(type)
    # accounts = get_app_config("accounts")
    accounts = get_data_list("accounts")
    account_dict = {account["Account"]: account for account in accounts}

    file_list = []
    for this_account, params in account_dict.items():
        if account and this_account != account:
            continue
        uid = params["uid"]
        path = os.path.join(filepath, uid)
        files = glob.glob(path + "/*.csv")
        files_CSV = glob.glob(path + "/*.CSV")
        files.extend(files_CSV)
        for filename in files:
            file_dict = {}
            file_dict["account"] = this_account
            file_dict["path"] = path
            file_dict["filename"] = filename
            file_list.append(file_dict)
    return file_list


def get_register_dataframe(account=None, filename=None):
    column_types = {"Category": "object"}
    date_columns = ["Date"]
    if filename:
        file_list = [{"filename": filename}]
    else:
        file_list = get_statement_files(type="register", account=account)
    df_list = []
    for file in file_list:
        filename = file["filename"]
        df = pd.read_csv(
            filename, index_col=None, dtype=column_types, parse_dates=date_columns
        )
        df_list.append(df)
    df = pd.concat(df_list, ignore_index=True)
    return df


def get_data_list(file_type):
    data_file_path = get_data_file_path(file_type)
    with open(data_file_path) as f:
        data_list = csv.DictReader(f)
        data_list = list(data_list)
    return data_list


def get_dataframe(file_type):
    data_file_path = get_data_file_path(file_type)
    df = pd.read_csv(data_file_path, index_col=None)
    return df


def add_update_delete_df(df: pd.DataFrame, data_key):
    change = st.session_state[data_key]
    for row, row_dict in change["edited_rows"].items():
        for key, value in row_dict.items():
            df.loc[row, key] = value

    column_names = list(df.columns)
    for row_dict in change["added_rows"]:
        if all([True if column in row_dict else False for column in column_names]):
            if "_index" in row_dict:
                row_dict.pop("_index")
            df.loc[len(df.index)] = row_dict.values()

    for row_index in change["deleted_rows"]:
        df.drop(row_index, inplace=True)
    data_file_path = get_data_file_path(data_key)
    df.to_csv(data_file_path, index=False, header=True)
    return True


def add_update_delete_register(df: pd.DataFrame, data_key, filename):
    change = st.session_state[data_key]
    for row, row_dict in change["edited_rows"].items():
        for key, value in row_dict.items():
            df.loc[row, key] = value
            df.to_csv(filename, index=False, header=True)
    return True


def get_budget_categories(type="Combined"):
    df = get_dataframe("budget")
    if type == "Combined":
        df["categories"] = df["Category 1"] + " | " + df["Category 2"]
        categories = df["categories"].tolist()
    elif type == "Category 1":
        categories = df["Category 1"].tolist()
    elif type == "Category 2":
        categories = df["Category 2"].tolist()
    return categories
