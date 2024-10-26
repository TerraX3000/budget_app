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
    """Displays bar chart of budget by month for each category"""
    category_totals = summarize_budget_by_category(budget)
    df = pd.DataFrame(category_totals)
    df = df.melt(id_vars="Category 1", var_name="Month", value_name="Amount")
    category_totals_sorted = (
        df.groupby("Category 1")["Amount"]
        .sum()
        .sort_values(ascending=False)
        .index.tolist()
    )
    df = df.sort_values(["Category 1", "Month"])
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

    # Sort the categories by alphabetical order
    category_totals_sorted_alphabetical = sorted(category_totals_sorted)

    # Assign rainbow colors to the categories sorted in alphabetical order
    colors = rainbow(len(category_totals_sorted_alphabetical))

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("Month", sort=month_order),
            y="Amount",
            color=alt.Color(
                "Category 1:N",
                scale=alt.Scale(
                    domain=category_totals_sorted_alphabetical, range=colors
                ),
            ),
            tooltip=["Month", "Amount", "Category 1"],
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
