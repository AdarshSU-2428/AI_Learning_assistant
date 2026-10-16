import logging
import streamlit as st

from frontend.ui.api_client import APIClient
from frontend.ui.sidebar import SidebarManager
from frontend.ui.components import (
    render_header,
    render_learning_about,
    render_user_message,
    render_assistant_message,
    get_user_friendly_error_message,
    render_error,
)

logger = logging.getLogger(__name__)


def render_learning_interface(api_client):
    """
    Renders the dedicated Learning Mode conversational interface.
    Displays the About section initially, replacing it dynamically with the active
    chat stream as soon as questions are asked.
    """
    SidebarManager.render_learning_sidebar()
    render_header(
        title="🎓 Learning Mode",
        subtitle="Ask conceptual questions grounded strictly in your course lecture slides and textbooks"
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display About section if no conversation history exists
    if not st.session_state.messages:
        render_learning_about()
    else:
        # Render active conversation history
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                render_user_message(msg["content"])
            elif msg["role"] == "assistant":
                render_assistant_message(msg["content"], msg.get("sources"))

    # Chat input box
    prompt = st.chat_input("Ask a concept question about your study materials...")

    if prompt is not None:
        cleaned_prompt = prompt.strip()
        if not cleaned_prompt:
            render_error("Please enter a valid question.")
            return

        # Append and display user message immediately
        st.session_state.messages.append({"role": "user", "content": cleaned_prompt})
        render_user_message(cleaned_prompt)

        # Call APIClient inside thinking state
        with st.spinner("Analyzing lecture notes and preparing response..."):
            try:
                selected_subject = st.session_state.get("selected_subject")
                response = api_client.send_message(cleaned_prompt, subject=selected_subject)
                answer = response.get("answer", "")
                sources = response.get("sources", [])

                # Store assistant response in session state
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    }
                )

                # Rerun to update chat display cleanly
                st.rerun()

            except Exception as exc:
                logger.error("API request failed: %s", exc, exc_info=True)
                user_msg = get_user_friendly_error_message(exc)
                render_error(user_msg)
