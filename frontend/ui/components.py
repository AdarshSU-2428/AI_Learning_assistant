import os
import re
import streamlit as st

from frontend.ui.api_client import (
    APIClientError,
    BackendConnectionError,
    BackendTimeoutError,
    BackendResponseError,
    InvalidBackendResponseError,
)


def inject_custom_css():
    """Injects custom CSS to style the Streamlit interface with modern aesthetics."""
    css = """
    <style>
        /* Main background and font styling */
        .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* App Header styling */
        .app-header {
            padding: 1.2rem 0 0.5rem 0;
            margin-bottom: 1.5rem;
            border-bottom: 1px solid rgba(128, 128, 128, 0.2);
        }
        
        .app-header h1 {
            font-size: 2.2rem;
            font-weight: 700;
            margin: 0;
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .app-header p {
            color: #6b7280;
            font-size: 1rem;
            margin-top: 0.25rem;
        }

        /* Card container styling */
        .welcome-card {
            background-color: rgba(243, 244, 246, 0.6);
            border: 1px solid rgba(229, 231, 235, 0.8);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        
        @media (prefers-color-scheme: dark) {
            .welcome-card {
                background-color: rgba(31, 41, 55, 0.5);
                border: 1px solid rgba(55, 65, 81, 0.8);
            }
        }

        /* Suggestion pill styling */
        .suggestion-header {
            font-weight: 600;
            font-size: 0.9rem;
            color: #4b5563;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }

        /* Custom badge for sources */
        .source-badge {
            display: inline-block;
            background-color: rgba(37, 99, 235, 0.1);
            color: #2563eb;
            border: 1px solid rgba(37, 99, 235, 0.2);
            border-radius: 6px;
            padding: 0.2rem 0.5rem;
            font-size: 0.85rem;
            margin-right: 0.5rem;
            margin-bottom: 0.4rem;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_header():
    """Renders the main application header."""
    st.markdown(
        """
        <div class="app-header">
            <h1>🎓 AI Learning Assistant</h1>
            <p>Your interactive study companion for quick explanations and document insights</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_welcome_state():
    """Renders a friendly welcome message for empty chat state."""
    st.markdown(
        """
        <div class="welcome-card">
            <h3>Welcome to your AI Learning Assistant! 👋</h3>
            <p>I'm here to help you understand your study materials, clarify concepts, and answer your questions accurately based on your course documents.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def parse_source_info(source_item):
    """
    Extracts a user-friendly (filename, unit_info) tuple from various source representations.
    unit_info is ("Page", page_num) or ("Slide", slide_num) or None.
    """
    metadata = {}
    if isinstance(source_item, dict):
        if "metadata" in source_item and isinstance(source_item["metadata"], dict):
            metadata = source_item["metadata"]
        else:
            metadata = source_item
    elif isinstance(source_item, str):
        metadata = {"source": source_item}

    raw_source = (
        metadata.get("source")
        or metadata.get("filename")
        or metadata.get("file_name")
        or metadata.get("title")
        or metadata.get("file_path")
        or ""
    )

    if not raw_source and isinstance(source_item, str):
        raw_source = source_item

    if not raw_source or not isinstance(raw_source, str):
        return None

    clean_filename = os.path.basename(raw_source.replace("\\", "/"))
    if not clean_filename or clean_filename.strip() in ("", ".", ".."):
        return None

    page = metadata.get("page") if "page" in metadata else metadata.get("page_number")
    slide = (
        metadata.get("slide") if "slide" in metadata else metadata.get("slide_number")
    )

    unit_info = None
    if page is not None:
        try:
            unit_info = ("Page", int(page))
        except (ValueError, TypeError):
            if str(page).strip():
                unit_info = ("Page", str(page))
    elif slide is not None:
        try:
            unit_info = ("Slide", int(slide))
        except (ValueError, TypeError):
            if str(slide).strip():
                unit_info = ("Slide", str(slide))

    return clean_filename, unit_info


def render_sources(sources):
    """Renders document sources cleanly in an expandable section if present."""
    if not sources or not isinstance(sources, list):
        return

    file_units = {}

    for item in sources:
        parsed = parse_source_info(item)
        if not parsed:
            continue
        filename, unit_info = parsed
        if filename not in file_units:
            file_units[filename] = {}

        if unit_info:
            unit_type, unit_num = unit_info
            if unit_type not in file_units[filename]:
                file_units[filename][unit_type] = []
            if unit_num not in file_units[filename][unit_type]:
                file_units[filename][unit_type].append(unit_num)

    if not file_units:
        return

    with st.expander("📚 Sources & References", expanded=False):
        for filename, units in file_units.items():
            if not units:
                st.markdown(f"- 📄 **{filename}**")
            else:
                unit_strings = []
                for unit_type, nums in units.items():
                    sorted_nums = sorted(nums, key=lambda x: (isinstance(x, str), x))
                    nums_str = ", ".join(str(n) for n in sorted_nums)
                    label = f"{unit_type}s" if len(sorted_nums) > 1 else unit_type
                    unit_strings.append(f"{label} {nums_str}")

                details = " — " + "; ".join(unit_strings) if unit_strings else ""
                st.markdown(f"- 📄 **{filename}**{details}")


def render_user_message(content):
    """Renders a user chat message bubble."""
    with st.chat_message("user"):
        st.markdown(content)


def render_assistant_message(content, sources):
    """Renders an assistant chat message bubble with optional sources."""
    with st.chat_message("assistant"):
        st.markdown(content)
        if sources:
            render_sources(sources)


def get_user_friendly_error_message(exc):
    """
    Translates technical exceptions into product-level user messages.
    Excludes technical jargon (backend, FastAPI, HTTP codes, tracebacks).
    """
    if isinstance(exc, BackendConnectionError):
        return "AI Learning Assistant is temporarily unavailable. Please try again shortly."

    if isinstance(exc, BackendTimeoutError):
        return "The response is taking longer than expected. Please try again."

    if isinstance(exc, InvalidBackendResponseError):
        return "Something went wrong while preparing the response. Please try again."

    if isinstance(exc, BackendResponseError):
        err_str = str(exc).lower()
        if "question" in err_str or "empty" in err_str or "valid" in err_str:
            return "Please enter a valid question."
        return "Something went wrong while preparing the response. Please try again."

    if isinstance(exc, ValueError):
        err_str = str(exc).lower()
        if "question" in err_str or "empty" in err_str or "valid" in err_str:
            return "Please enter a valid question."
        return "Something went wrong. Please try again."

    return "Something went wrong. Please try again."


def render_error(message):
    """Renders a user-friendly error message container."""
    st.error(message, icon="⚠️")
