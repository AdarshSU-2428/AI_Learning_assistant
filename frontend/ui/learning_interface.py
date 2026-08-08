import logging
import streamlit as st

from frontend.ui.api_client import APIClient
from frontend.ui.sidebar import render_sidebar
from frontend.ui.components import (
    render_header,
    render_welcome_state,
    render_user_message,
    render_assistant_message,
    get_user_friendly_error_message,
    render_error,
)

logger = logging.getLogger(__name__)


def render_learning_interface(api_client):
    """
    Renders the dedicated Learning Mode conversational interface, managing
    session state, prompt inputs, API client calls, loading states, and error handling.
    """
    render_sidebar()
    render_header()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display empty welcome state if no conversation history exists
    if not st.session_state.messages:
        render_welcome_state()
    else:
        # Render conversation history
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                render_user_message(msg["content"])
            elif msg["role"] == "assistant":
                render_assistant_message(msg["content"], msg.get("sources"))

    # Chat input box
    prompt = st.chat_input("Ask a question about your study materials...")

    if prompt is not None:
        cleaned_prompt = prompt.strip()
        if not cleaned_prompt:
            render_error("Please enter a valid question.")
            return

        # Append and display user message immediately
        st.session_state.messages.append({"role": "user", "content": cleaned_prompt})
        render_user_message(cleaned_prompt)

        # Call APIClient inside thinking state
        with st.spinner("Thinking..."):
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
