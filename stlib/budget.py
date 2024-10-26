import streamlit as st
from streamlit_datatables_net import (
    st_datatable,
    stringify_javascript_function,
    stringify_file,
)
import pandas as pd
from sections import navbar
from functions.utility import (
    get_data_file_path,
    get_data_list,
)
import os
from typing import List, Dict

JAVASCRIPT_FILE_PATH = "functions/datatable_functions.js"


def write_annual_budget_to_csv_file(budget: List[Dict]):
    df = pd.DataFrame(budget)
    file_path = get_data_file_path("annual_budgets")
    year = st.session_state["year"]
    if year:
        file_path += f"/annual_budget_{year}.csv"
        df.to_csv(file_path, index=False)


def get_category_options():
    budget = get_data_list("budget")
    for item in budget:
        item["Jan"] = 0
        item["Feb"] = 0
        item["Mar"] = 0
        item["Apr"] = 0
        item["May"] = 0
        item["Jun"] = 0
        item["Jul"] = 0
        item["Aug"] = 0
        item["Sep"] = 0
        item["Oct"] = 0
        item["Nov"] = 0
        item["Dec"] = 0
    return budget


def get_columns():
    render_input = stringify_javascript_function(
        JAVASCRIPT_FILE_PATH, "render_input_cell"
    )
    columns = [
        {
            "data": "Category 1",
            "title": "Category 1",
        },
        {
            "data": "Category 2",
            "title": "Category 2",
        },
        {
            "data": "Jan",
            "title": "Jan",
            "render": render_input,
        },
        {
            "data": "Feb",
            "title": "Feb",
            "render": render_input,
        },
        {
            "data": "Mar",
            "title": "Mar",
            "render": render_input,
        },
        {
            "data": "Apr",
            "title": "Apr",
            "render": render_input,
        },
        {
            "data": "May",
            "title": "May",
            "render": render_input,
        },
        {
            "data": "Jun",
            "title": "Jun",
            "render": render_input,
        },
        {
            "data": "Jul",
            "title": "Jul",
            "render": render_input,
        },
        {
            "data": "Aug",
            "title": "Aug",
            "render": render_input,
        },
        {
            "data": "Sep",
            "title": "Sep",
            "render": render_input,
        },
        {
            "data": "Oct",
            "title": "Oct",
            "render": render_input,
        },
        {
            "data": "Nov",
            "title": "Nov",
            "render": render_input,
        },
        {
            "data": "Dec",
            "title": "Dec",
            "render": render_input,
        },
    ]
    return columns


def get_datatable_options():
    options = {}
    options["columns"] = get_columns()
    on_click_submit_table_values = stringify_javascript_function(
        JAVASCRIPT_FILE_PATH, "on_click_submit_table_values"
    )

    return_table_values_button = {
        "text": "Save Budget Changes",
        "action": on_click_submit_table_values,
    }
    excel = (
        {
            "extend": "excel",
            "text": "Export to Excel",
            "exportOptions": {"orthogonal": "export"},
        },
    )

    options["buttons"] = [
        excel,
        return_table_values_button,
    ]
    options["layout"] = {"topStart": "buttons", "topEnd": None}
    options["scrollY"] = "600px"
    options["scrollX"] = False
    options["paging"] = False
    options["ordering"] = False
    options["info"] = False
    return options


def on_click_handler(key):
    if (
        "customComponentValue" in st.session_state[key]
        and "allValues" in st.session_state[key]["customComponentValue"]
    ):
        budget = st.session_state[key]["customComponentValue"]["allValues"]
        st.session_state["budget"] = budget
        write_annual_budget_to_csv_file(budget)


def show_datatable():
    options = get_datatable_options()
    budget = st.session_state["budget"]
    export_file_name = f"Annual Budget - {st.session_state['year']}"
    css_files = [stringify_file("static/datatable.css")]
    st_datatable(
        budget,
        options=options,
        on_select=on_click_handler,
        css_files=css_files,
        args=["budget_table"],
        key="budget_table",
        export_file_name=export_file_name,
    )


def initialize_session_state():
    st.session_state["initialized"] = True


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
    if not budget:
        budget = get_category_options()
    st.session_state["budget"] = budget


def set_state():
    year = st.session_state["year"]
    st.session_state["page:budget"]["year"] = year


def on_year_change():
    set_budget_in_session()
    set_state()


def run():
    st.query_params.page = "budget"
    navbar.run()
    if "page:budget" not in st.session_state:
        st.session_state["page:budget"] = {}
        st.session_state["page:budget"]["year"] = None
    years = ["2024", "2025"]
    col_1, col_2, col_3 = st.columns([2, 2, 4])
    if st.session_state["page:budget"]["year"]:
        index = years.index(st.session_state["page:budget"]["year"])
    else:
        index = None
    print(index)
    year = col_1.selectbox(
        "Select year",
        options=years,
        index=index,
        key="year",
        on_change=on_year_change,
    )
    if year:
        show_datatable()
