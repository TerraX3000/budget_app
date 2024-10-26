import streamlit as st
import pandas as pd
from sections import navbar
from functions.utility import (
    get_data_file_path,
    get_data_list,
)
import os
from typing import List, Dict
import altair as alt
import colorsys


def summarize_budget_by_category(budget):
    category_totals = {}
    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    for item in budget:
        category = item["Category 1"]
        if category not in category_totals:
            category_totals[category] = {"Category 1": category}
            for month in months:
                category_totals[category][month] = 0
        for month in months:
            category_totals[category][month] += item[month]
    return list(category_totals.values())


def get_budget_from_csv_file(year):
    file_path = get_data_file_path("annual_budgets")
    file_path += f"/annual_budget_{year}.csv"
    if not os.path.exists(file_path):
        return None
    df = pd.read_csv(file_path)
    budget = df.to_dict(orient="records")
    return budget


def set_budget_in_session():
    budget = get_budget_from_csv_file(st.session_state["year"])
    st.session_state["budget"] = budget


def set_state():
    year = st.session_state["year"]
    st.session_state["page:analysis"]["year"] = year


def on_year_change():
    set_budget_in_session()
    set_state()


def rainbow(n):
    return [
        "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))
        for r, g, b in [colorsys.hsv_to_rgb(h, 1, 1) for h in [i / n for i in range(n)]]
    ]


def display_bar_chart_of_budget_by_category(budget):
    """Displays bar chart of budget by month with categories sorted by cumulative total amount."""
    category_totals = summarize_budget_by_category(budget)
    df = pd.DataFrame(category_totals)
    df = df.melt(id_vars="Category 1", var_name="Month", value_name="Amount")

    # Calculate cumulative total for each category across all months and sort
    category_totals_sorted = (
        df.groupby("Category 1")["Amount"]
        .sum()
        .sort_values(ascending=True)  # Sort in ascending order by cumulative amount
        .index.tolist()
    )
    # Ensure the DataFrame respects the sorted order by cumulative amount
    df["Category 1"] = pd.Categorical(
        df["Category 1"], categories=category_totals_sorted, ordered=True
    )
    month_order = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    df["Month"] = pd.Categorical(df["Month"], categories=month_order, ordered=True)

    # Assign rainbow colors to categories in alphabetical order for color consistency
    category_totals_alphabetical = sorted(df["Category 1"].unique())
    colors = rainbow(len(category_totals_alphabetical))

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("Month", sort=month_order),
            y="Amount",
            color=alt.Color(
                "Category 1:N",
                scale=alt.Scale(
                    domain=category_totals_alphabetical,
                    range=colors,  # Assign colors by alphabetical order
                ),
            ),
            tooltip=["Month", "Amount", "Category 1"],
        )
    )
    st.altair_chart(chart, use_container_width=True)


def display_bar_chart_of_annual_total_by_category(budget):
    category_totals = summarize_budget_by_category(budget)
    df = pd.DataFrame(category_totals)
    df = df.melt(id_vars="Category 1", var_name="Month", value_name="Amount")

    # Calculate the total amount spent by each category for the entire year
    df_annual_total = df.groupby("Category 1")["Amount"].sum().reset_index()

    # Sort the categories by alphabetical order
    category_totals_sorted_alphabetical = sorted(df_annual_total["Category 1"].unique())

    # Assign rainbow colors to the categories sorted in alphabetical order
    colors = rainbow(len(category_totals_sorted_alphabetical))

    chart = (
        alt.Chart(df_annual_total)
        .mark_bar()
        .encode(
            x=alt.X("Category 1:N", sort=category_totals_sorted_alphabetical),
            y="Amount",
            color=alt.Color(
                "Category 1:N",
                scale=alt.Scale(
                    domain=category_totals_sorted_alphabetical, range=colors
                ),
            ),
            tooltip=["Category 1", "Amount"],
        )
    )
    st.altair_chart(chart, use_container_width=True)


def run():
    st.query_params.page = "analysis"
    navbar.run()
    if "page:analysis" not in st.session_state:
        st.session_state["page:analysis"] = {}
        st.session_state["page:analysis"]["year"] = None

    years = ["2024", "2025"]
    col_1, col_2, col_3 = st.columns([2, 2, 4])
    if st.session_state["page:analysis"]["year"]:
        index = years.index(st.session_state["page:analysis"]["year"])
    else:
        index = None
    year = col_1.selectbox(
        "Select year",
        options=years,
        index=index,
        key="year",
        on_change=on_year_change,
    )
    if year:
        budget = st.session_state["budget"]
        display_bar_chart_of_budget_by_category(budget)
        display_bar_chart_of_annual_total_by_category(budget)
