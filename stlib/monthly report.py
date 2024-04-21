import streamlit as st
import pandas as pd
import glob
from sections import navbar
from functions.utility import get_register_dataframe, get_data_list
from icecream import ic


def run():
    st.query_params.page = "monthly report"
    navbar.run()

    with st.container():
        year_column, spacer = st.columns([2, 10])
        with year_column:
            desired_year = st.selectbox("Year", options=[2024])
        df = get_register_dataframe()
        budget = get_data_list("budget")
        categories_to_exclude = [
            f'{item["Category 1"]}:{item["Category 2"]}'
            for item in budget
            if item["Include in Report"] == "False"
        ]
        df = df[~df["Category"].isin(categories_to_exclude)]

        df = df[df["Date"].dt.year == desired_year]

        df["Month"] = df["Date"].dt.month_name()
        month_order = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        df["Month"] = pd.Categorical(df["Month"], categories=month_order, ordered=True)

        pivot_table = df.pivot_table(
            index="Category",
            columns="Month",
            values="Amount",
            aggfunc="sum",
            fill_value=0,
        )
        st.dataframe(
            pivot_table, use_container_width=True, height=38 * len(pivot_table)
        )
