import sys
from pathlib import Path

# Ensure root directory is in sys.path when imported from root app.py
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
from frontend.ui.api_client import APIClient
from frontend.ui.components import inject_custom_css
from frontend.ui.sidebar import render_sidebar
from frontend.ui.chat_interface import render_chat_interface

# Streamlit Page Configuration
st.set_page_config(
    page_title="AI Learning Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    inject_custom_css()
    api_client = APIClient(base_url=None)
    render_sidebar()
    render_chat_interface(api_client)
