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
            padding: 1rem 0 0.5rem 0;
            margin-bottom: 1.2rem;
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

        /* Feature Card styling */
        .about-card {
            background-color: rgba(243, 244, 246, 0.6);
            border: 1px solid rgba(229, 231, 235, 0.9);
            border-radius: 12px;
            padding: 1.4rem;
            margin-bottom: 1.2rem;
            transition: all 0.2s ease-in-out;
        }
        
        @media (prefers-color-scheme: dark) {
            .about-card {
                background-color: rgba(31, 41, 55, 0.5);
                border: 1px solid rgba(55, 65, 81, 0.8);
            }
        }

        .about-card h3 {
            margin-top: 0;
            color: #1f2937;
            font-size: 1.25rem;
        }

        @media (prefers-color-scheme: dark) {
            .about-card h3 {
                color: #f3f4f6;
            }
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

        .quick-chip {
            display: inline-block;
            padding: 0.35rem 0.75rem;
            background: rgba(37, 99, 235, 0.08);
            border: 1px solid rgba(37, 99, 235, 0.2);
            border-radius: 20px;
            font-size: 0.85rem;
            color: #2563eb;
            margin: 0.25rem;
        }
        .mode-card-list {
            padding-left: 1.2rem;
            margin-bottom: 0;
            line-height: 1.6;
        }

        .mode-card-list li {
            margin-bottom: 0.4rem;
        }

        /* Complete Flexbox stretching for equal card heights */
        div[data-testid="stHorizontalBlock"] {
            align-items: stretch !important;
        }

        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            display: flex !important;
            flex-direction: column !important;
        }

        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div[data-testid="stVerticalBlock"] {
            display: flex !important;
            flex-direction: column !important;
            flex: 1 1 auto !important;
            height: 100% !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            display: flex !important;
            flex-direction: column !important;
            flex: 1 1 auto !important;
            height: 100% !important;
            border-radius: 12px !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            display: flex !important;
            flex-direction: column !important;
            flex: 1 1 auto !important;
            justify-content: space-between !important;
            height: 100% !important;
        }

        /* Pin all card action buttons to the absolute bottom */
        div[data-testid="stVerticalBlockBorderWrapper"] .stButton {
            margin-top: auto !important;
            padding-top: 1.2rem !important;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_header(title="🎓 AI Learning Assistant", subtitle="Your autonomous university study companion grounded strictly in course documents"):
    """Renders the main application header."""
    st.markdown(
        f"""
        <div class="app-header">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_home_about():
    """Renders the comprehensive About section on the Hub landing page."""
    st.markdown(
        """
        <div class="about-card">
            <h3>🌟 Welcome to AI Learning Assistant</h3>
            <p>
                The <strong>AI Learning Assistant</strong> is an autonomous, syllabus-grounded engineering study platform designed to help students master complex course materials, verify practical lab implementations, and test exam readiness with high precision.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; flex-direction: column; flex: 1 1 auto;">
                    <h4 style="margin-top: 0; margin-bottom: 0.6rem; font-size: 1.15rem; font-weight: 700;">🎓 Learning Mode</h4>
                    <ul class="mode-card-list">
                        <li><strong>Concept Q&A</strong> with lecture slides & notes</li>
                        <li><strong>Exact Citations</strong> with slide & page numbers</li>
                        <li><strong>Algorithmic Tracing</strong> & LaTeX formulas</li>
                        <li><strong>Syllabus Shielding</strong> against out-of-scope queries</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Open Learning Mode ➔", key="home_btn_learn", type="primary", use_container_width=True):
                st.session_state.active_mode = "learning"
                st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; flex-direction: column; flex: 1 1 auto;">
                    <h4 style="margin-top: 0; margin-bottom: 0.6rem; font-size: 1.15rem; font-weight: 700;">🎯 Quiz Mode</h4>
                    <ul class="mode-card-list">
                        <li><strong>Interactive MCQ Studio</strong> from question bank</li>
                        <li><strong>Dynamic Difficulty</strong> (Easy, Medium, Hard)</li>
                        <li><strong>Custom Counts</strong> from 3 up to 30 questions</li>
                        <li><strong>Auto-Grading</strong> with hints & explanations</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Open Quiz Mode ➔", key="home_btn_quiz", type="primary", use_container_width=True):
                st.session_state.active_mode = "quiz"
                st.rerun()

    with col3:
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; flex-direction: column; flex: 1 1 auto;">
                    <h4 style="margin-top: 0; margin-bottom: 0.6rem; font-size: 1.15rem; font-weight: 700;">🧪 Lab Mode</h4>
                    <ul class="mode-card-list">
                        <li><strong>Runnable Programs</strong> with test cases & complexity</li>
                        <li><strong>Circuit Walkthroughs</strong> & pinout diagrams</li>
                        <li><strong>Observation Tables</strong> & error formulas</li>
                        <li><strong>Viva Voce Oral Prep</strong> with model answers</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Open Lab Mode ➔", key="home_btn_lab", type="primary", use_container_width=True):
                st.session_state.active_mode = "lab"
                st.rerun()

    with col4:
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; flex-direction: column; flex: 1 1 auto;">
                    <h4 style="margin-top: 0; margin-bottom: 0.6rem; font-size: 1.15rem; font-weight: 700;">📝 Exam Mode</h4>
                    <ul class="mode-card-list">
                        <li><strong>PYQ Exam Papers</strong> (1, 3, 5 Marks)</li>
                        <li><strong>Random Shuffling</strong> of syllabus questions</li>
                        <li><strong>Physical Paper Practice</strong> workflow</li>
                        <li><strong>Model Answers & Rubrics</strong> for self-rating</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Open Exam Mode ➔", key="home_btn_exam", type="primary", use_container_width=True):
                st.session_state.active_mode = "exam"
                st.rerun()

    st.markdown("---")

    with st.container(border=True):
        st.markdown("### 🛡️ Grounding & System Architecture")
        c_arch1, c_arch2 = st.columns(2)
        with c_arch1:
            st.markdown("""
            - 🔍 **Hybrid Retrieval Engine**: Powered by `BAAI/bge-base-en-v1.5` dense embeddings and ChromaDB vector indexing.
            - 🎯 **Cross-Encoder Reranker**: Employs `ms-marco-MiniLM-L-6-v2` for precise semantic scoring.
            """)
        with c_arch2:
            st.markdown("""
            - 🚦 **Relevance Gate**: Automatically filters out hallucinated or out-of-syllabus responses.
            - 🔒 **Instruction Shielding**: Advanced safety managers shield against prompt injections.
            """)


def render_learning_about():
    """Renders the About card for Learning Mode when no chat activity has started."""
    st.markdown(
        """
        <div class="about-card">
            <h3>📖 About Learning Mode</h3>
            <p>
                Learning Mode serves as your autonomous course tutor. Ask questions about theoretical concepts, architectural diagrams, mathematical derivations, or textbook chapters. Every answer is grounded directly in your uploaded lecture notes and slides with verified page citations.
            </p>
            <div style="margin-top: 0.8rem;">
                <strong>💡 How to use:</strong>
                <ol style="margin-top: 0.3rem; padding-left: 1.2rem;">
                    <li>Select your course subject from the <strong>left sidebar</strong>.</li>
                    <li>Type any conceptual question or topic in the chat box below.</li>
                    <li>Inspect the <em>Sources & References</em> expander beneath each answer for slide numbers.</li>
                </ol>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_quiz_about():
    """Renders the About card for Quiz Mode before a quiz is generated."""
    st.markdown(
        """
        <div class="about-card">
            <h3>🎯 About Quiz Mode</h3>
            <p>
                Quiz Mode is your interactive self-assessment studio. Generate targeted multiple-choice question sets pulled from verified university subject repositories to test your conceptual recall and problem-solving speed.
            </p>
            <div style="margin-top: 0.8rem;">
                <strong>⚙️ How to get started:</strong>
                <ol style="margin-top: 0.3rem; padding-left: 1.2rem;">
                    <li>Configure your <strong>Subject</strong>, <strong>Difficulty</strong>, and <strong>Number of Questions</strong> in the left sidebar.</li>
                    <li>Click <strong>🚀 Generate Quiz</strong> in the sidebar.</li>
                    <li>Submit your choices to view your percentage score, hints, and step-by-step answer explanations!</li>
                </ol>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_lab_about():
    """Renders the About card for Lab Mode before conversation starts."""
    st.markdown(
        """
        <div class="about-card">
            <h3>🧪 About Practical Lab Mode</h3>
            <p>
                Lab Mode is specifically optimized for engineering practicals, coding experiments, laboratory manuals, and viva voce preparation. Whether you need complete runnable code, hardware pinouts, observation table formulas, or viva questions, Lab Mode provides structured practical solutions.
            </p>
            <div style="margin-top: 0.8rem;">
                <strong>🔬 Practical Capabilities:</strong>
                <ul style="margin-top: 0.3rem; padding-left: 1.2rem;">
                    <li><strong>Coding Practicals:</strong> Complete, copyable programs with edge cases, sample I/O, and time/space complexity analysis.</li>
                    <li><strong>Hardware & Electronics:</strong> Circuit diagrams, truth tables, IC pinouts, and Boolean simplifications.</li>
                    <li><strong>Calculations & Observations:</strong> Tabular experimental readings and percentage error formulas.</li>
                    <li><strong>Viva Voce Prep:</strong> High-yield oral exam questions with concise model answers.</li>
                </ul>
            </div>
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
