import streamlit as st
import pandas as pd
import glob
from sections import navbar
from functions.utility import get_register_dataframe, get_app_config, get_data_list
import datetime
from icecream import ic
from typing import List


def expenditures_metric(df):
    expenses_df = df[~df["Category"].str.startswith("Transfer", na=False)]
    expenses_df = expenses_df.query(f"Amount < 0")
    expenditures = abs(expenses_df["Amount"].sum())
    st.metric("Total Expenditures", f"${expenditures:,.0f}")


def income_metric(df):
    income_df = df[df["Category"].str.startswith("Income", na=False)]
    income_df = income_df.query(f"Amount > 0")
    income = income_df["Amount"].sum()
    st.metric("Income", f"${income:,.0f}")


def category_metrics(df):
    with st.expander("Expenditure Categories"):
        row_1 = st.columns([1, 1, 1, 1, 1, 1, 1])
        row_2 = st.columns([1, 1, 1, 1, 1, 1, 1])
        row_3 = st.columns([1, 1, 1, 1, 1, 1, 1])
    categories = df["Category"].drop_duplicates().sort_values().to_list()
    categories = set([(str(category).split("|")[0]).strip() for category in categories])
    if "nan" in categories:
        categories.remove("nan")
    if "Transfer" in categories:
        categories.remove("Transfer")
    if "Income" in categories:
        categories.remove("Income")
    category_sums = []
    for category in categories:
        dff = df.copy()
        dff = dff[dff["Category"].str.startswith(category, na=False)]
        sum = abs(dff["Amount"].sum())
        category_sum = {"category": category, "sum": sum}
        category_sums.append(category_sum)
    sorted_list = sorted(category_sums, key=lambda x: x["sum"], reverse=True)
    for column, category_sum in zip(row_1 + row_2 + row_3, sorted_list):
        with column:
            st.metric(category_sum["category"], f"${abs(category_sum['sum']):,.0f}")


def set_state(key, options: List):
    index = options.index(st.session_state[key])
    st.session_state["expenses"][key] = index
    if key == "category":
        st.session_state["expenses"]["sub_category"] = 0


def run():
    st.query_params.page = "expenses"
    if "expenses" not in st.session_state:
        st.session_state["expenses"] = {}
        st.session_state["expenses"]["accounts"] = None
        today = datetime.date.today()
        jan_1st = datetime.date(today.year, 1, 1)
        st.session_state["expenses"]["start_date"] = jan_1st
        st.session_state["expenses"]["end_date"] = today
        st.session_state["expenses"]["category"] = 0
        st.session_state["expenses"]["sub_category"] = 0
        st.session_state["expenses"]["search_text"] = None
    navbar.run()
    df = get_register_dataframe()
    df = df.sort_values(["Date", "Account"], ascending=[True, True])
    budget = get_data_list("budget")
    category_1_list = sorted(set([item["Category 1"] for item in budget]))
    category_1_list.insert(0, "")

    with st.container():
        st.write("")
        col_1, col_2, col_3, col_4 = st.columns([1, 1, 1, 1])
        col_5, col_6 = st.columns([4, 2])
        with col_1:

            start_date = st.date_input(
                "Start Date",
                value=st.session_state["expenses"]["start_date"],
                format="MM/DD/YYYY",
            )
            st.session_state["expenses"]["start_date"] = start_date
        with col_2:
            end_date = st.date_input(
                "End Date",
                value=st.session_state["expenses"]["end_date"],
                format="MM/DD/YYYY",
            )
            st.session_state["expenses"]["end_date"] = end_date
        df = df.query(f"Date >= '{start_date}' and Date < '{end_date}'")
        with col_3:
            options = category_1_list
            category = st.selectbox(
                "Category",
                key="category",
                options=options,
                index=st.session_state["expenses"]["category"],
                on_change=set_state,
                kwargs={"key": "category", "options": options},
            )
            if category:
                df = df[df["Category"].str.startswith(category, na=False)]
        with col_4:
            options = list(df["Category"].drop_duplicates().sort_values())
            options.insert(0, "")
            if st.session_state["expenses"]["sub_category"] < len(options):
                index = st.session_state["expenses"]["sub_category"]
            else:
                index = 0
            sub_category = st.selectbox(
                "Sub-Category",
                options=options,
                key="sub_category",
                index=index,
                on_change=set_state,
                kwargs={"key": "sub_category", "options": options},
            )
            if sub_category:
                df = df[df["Category"] == sub_category]
        with col_5:
            try:
                accounts = get_data_list("accounts")
            except:
                accounts = []
            if not accounts:
                st.warning("Add accounts before importing files.")
            account_dict = {account["Account"]: account for account in accounts}
            options = account_dict.keys()
            accounts = st.multiselect(
                "Account",
                options=options,
                default=st.session_state["expenses"]["accounts"],
            )
            st.session_state["expenses"]["accounts"] = accounts
            if accounts:
                df = df[df["Account"].isin(accounts)]
        with col_6:
            search_text = st.text_input(
                "Search Description", value=st.session_state["expenses"]["search_text"]
            )
            st.session_state["expenses"]["search_text"] = search_text
            if search_text:
                df = df[df["Description"].str.contains(search_text, case=False)]
        column_order = list(df.columns)

        st.write("")
        col_1, col_2, col_3, spacer = st.columns([2, 3, 2, 6])
        with col_1:
            st.metric("Transactions", len(df))
        with col_2:
            expenditures_metric(df)
        with col_3:
            income_metric(df)
        category_metrics(df)

        st.dataframe(
            df,
            column_order=column_order,
            use_container_width=True,
            hide_index=True,
            height=38 * len(df) + 38,
            column_config={
                "Date": st.column_config.DateColumn(
                    "Date",
                    format="MMMM D, YYYY",
                ),
                "Amount": st.column_config.NumberColumn(
                    "Amount",
                    help="Monthly budget amount",
                    format="%.2f",
                ),
            },
        )

        st.json(st.session_state)
