import streamlit as st
import pandas as pd
from sections import navbar
from functions.utility import (
    get_app_config,
    add_update_delete_df,
    get_dataframe,
    get_data_file_path,
)
import os
from typing import List
from icecream import ic


def upload_file():
    filepath = get_data_file_path("budget")
    file = st.session_state["budget_file"]
    with open(filepath, "wb") as f:
        f.write(file.getvalue())
    st.session_state["upload_budget_file"] = True


def upload_budget_file():
    filepath = get_data_file_path("budget")
    is_file = os.path.isfile(filepath)
    fields = ["Category 1", "Category 2", "Type", "Amount", "Include in Report"]
    header = ",".join(fields)
    if not is_file:
        st.file_uploader("Upload Budget File", key="budget_file", on_change=upload_file)


def run():
    st.query_params.page = "budget"
    navbar.run()
    st.write()
    if "upload_budget_file" not in st.session_state:
        upload_budget_file()

    if "upload_budget_file" in st.session_state:
        df = get_dataframe("budget")

        df = df.sort_values(
            ["Include in Report", "Category 1", "Category 2"],
            ascending=[False, True, True],
        )
        with st.container():
            key = "budget"
            st.data_editor(
                df,
                use_container_width=True,
                key=key,
                height=38 * len(df),
                on_change=add_update_delete_df,
                kwargs={"df": df, "data_key": key},
                hide_index=True,
                num_rows="dynamic",
                column_order=(
                    "Category 1",
                    "Category 2",
                    "Type",
                    "Amount",
                    "Include in Report",
                ),
                column_config={
                    "Type": st.column_config.SelectboxColumn(
                        "Type",
                        help="Income or Expenditure",
                        options=["Income", "Expenditure", "Transfer"],
                    ),
                    "Amount": st.column_config.NumberColumn(
                        "Amount",
                        help="Monthly budget amount",
                        step=1,
                        format="$%d",
                    ),
                    "Include in Report": st.column_config.CheckboxColumn(
                        "Include in Report",
                        help="Include category in report",
                        default=False,
                    ),
                },
            )
