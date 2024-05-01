import streamlit as st
import pandas as pd
import glob
from sections import navbar
from functions.utility import (
    get_register_dataframe,
    get_data_list,
    get_budget_categories,
)
from icecream import ic


def set_category(combined_category: str):
    categories = get_budget_categories(type="Category 1")
    if isinstance(combined_category, str):
        for category in categories:
            if combined_category.startswith(category):
                return category
    else:
        return "None"


def run():
    st.query_params.page = "monthly report"
    navbar.run()

    with st.container():
        year_column, col_2, spacer = st.columns([2, 2, 8])
        with year_column:
            desired_year = st.selectbox("Year", options=[2024])
        with col_2:
            show_subcategories = st.toggle("Show subcategories", value=False)

        df = get_register_dataframe()
        budget = get_data_list("budget")
        categories_to_exclude = [
            f'{item["Category 1"]} | {item["Category 2"]}'
            for item in budget
            if item["Include in Report"] == "False"
        ]
        df = df[~df["Category"].isin(categories_to_exclude)]

        df = df[df["Date"].dt.year == desired_year]

        if not show_subcategories:
            df["Category"] = df["Category"].apply(set_category)

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
