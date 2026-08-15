import sys
from pathlib import Path

# Ensure root directory is in sys.path when imported from root app.py
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
from frontend.ui.api_client import APIClient
from frontend.ui.components import inject_custom_css, render_header, render_home_about
from frontend.ui.sidebar import SidebarManager
from frontend.ui.learning_interface import render_learning_interface
from frontend.ui.quiz_interface import render_quiz_interface
from frontend.ui.lab_interface import render_lab_interface

# Streamlit Page Configuration
st.set_page_config(
    page_title="AI Learning Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


def render_home_hub():
    """Renders the main interactive landing page with sidebar navigation and central About section."""
    SidebarManager.render_home_sidebar()
    render_header(
        title="🎓 AI Learning Assistant",
        subtitle="Your autonomous university study companion grounded strictly in course documents"
    )
    render_home_about()


def main():
    inject_custom_css()
    api_client = APIClient(base_url=None)

    # Initialize Active Mode State (defaults to 'home')
    if "active_mode" not in st.session_state:
        st.session_state.active_mode = "home"

    # Route to Selected Mode
    if st.session_state.active_mode == "learning":
        render_learning_interface(api_client)
    elif st.session_state.active_mode == "quiz":
        render_quiz_interface(api_client)
    elif st.session_state.active_mode == "lab":
        render_lab_interface(api_client)
    else:
        render_home_hub()


if __name__ == "__main__":
    main()
