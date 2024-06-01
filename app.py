import importlib
import streamlit as st
import uuid
from functions.utility import get_app_config
from sections.login import check_password

st.set_page_config(
    page_title="Budget App",
    layout="wide",
)

if "sid" not in st.session_state:
    st.session_state.sid = str(uuid.uuid4())

if not check_password():
    st.stop()

module_names = get_app_config(config_name="modules")
try:
    module_name = st.query_params["page"]
except:
    module_name = "index"

if module_name:
    if module_name in module_names:
        module = importlib.import_module(f"stlib.{module_name}")
        st.header("Budget App")
        module.run()
    else:
        st.error(
            f'Module named "{module_name}" not found.  Did you forget to add it to the config file?'
        )

if module_name is None:
    st.error("Did you forget to set the page?")
