import logging
import streamlit as st

from frontend.ui.api_client import APIClient
from frontend.ui.sidebar import SidebarManager
from frontend.ui.components import (
    render_header,
    render_lab_about,
    render_user_message,
    render_assistant_message,
    get_user_friendly_error_message,
    render_error,
)

logger = logging.getLogger(__name__)


def render_lab_interface(api_client):
    """
    Renders the dedicated Practical Lab Mode interface.
    Controls (Lab Subject Dropdown, Action buttons) live strictly in the sidebar.
    Displays the About Lab section initially, replacing it dynamically with the active
    chat stream as soon as practical questions or code requests are submitted.
    """
    SidebarManager.render_lab_sidebar()
    render_header(
        title="🧪 Practical Lab Mode",
        subtitle="Practical coding walkthroughs, circuit pinouts, observation tables, and viva voce prep"
    )

    if "lab_messages" not in st.session_state:
        st.session_state.lab_messages = []

    # Display About section if no lab conversation history exists
    if not st.session_state.lab_messages:
        render_lab_about()
    else:
        # Render active lab conversation history
        for msg in st.session_state.lab_messages:
            if msg["role"] == "user":
                render_user_message(msg["content"])
            elif msg["role"] == "assistant":
                render_assistant_message(msg["content"], msg.get("sources"))

    # Chat input box for practical queries
    prompt = st.chat_input("Ask about a lab experiment, code solution, circuit truth table, or viva question...")

    if prompt is not None:
        cleaned_prompt = prompt.strip()
        if not cleaned_prompt:
            render_error("Please enter a valid lab experiment or coding question.")
            return

        # Append and display user message immediately
        st.session_state.lab_messages.append({"role": "user", "content": cleaned_prompt})
        render_user_message(cleaned_prompt)

        # Call APIClient inside thinking state
        with st.spinner("Analyzing lab manual, code repositories, and generating practical response..."):
            try:
                selected_subject = st.session_state.get("selected_lab_subject")
                response = api_client.send_lab_message(cleaned_prompt, subject=selected_subject)
                answer = response.get("answer", "")
                sources = response.get("sources", [])

                # Store assistant response in session state
                st.session_state.lab_messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    }
                )

                # Rerun to update chat display cleanly
                st.rerun()

            except Exception as exc:
                logger.error("Lab API request failed: %s", exc, exc_info=True)
                user_msg = get_user_friendly_error_message(exc)
                render_error(user_msg)
