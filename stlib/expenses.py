import streamlit as st
import pandas as pd
import glob
from sections import navbar
from functions.utility import get_register_dataframe, get_app_config, get_data_list
import datetime
from icecream import ic


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


def run():
    st.query_params.page = "expenses"
    navbar.run()
    df = get_register_dataframe()
    df = df.sort_values(["Date", "Account"], ascending=[True, True])
    budget = get_data_list("budget")
    category_1_list = sorted(set([item["Category 1"] for item in budget]))

    with st.container():
        st.write("")
        col_1, col_2, col_3, col_4 = st.columns([1, 1, 1, 1])
        col_5, col_6 = st.columns([4, 2])
        with col_1:
            today = datetime.date.today()
            jan_1st = datetime.date(today.year, 1, 1)
            start_date = st.date_input(
                "Start Date",
                value=jan_1st,
                format="MM/DD/YYYY",
            )
        with col_2:
            end_date = st.date_input(
                "End Date",
                format="MM/DD/YYYY",
            )
        df = df.query(f"Date >= '{start_date}' and Date < '{end_date}'")
        with col_3:
            options = category_1_list
            category = st.selectbox("Category", options=options, index=None)
            if category:
                df = df[df["Category"].str.startswith(category, na=False)]
        with col_4:
            options = df["Category"].drop_duplicates().sort_values()
            sub_category = st.selectbox("Sub-Category", options=options, index=None)
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
            accounts = st.multiselect("Account", options=options)
            if accounts:
                df = df[df["Account"].isin(accounts)]
        with col_6:
            search_text = st.text_input("Search Description")
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
