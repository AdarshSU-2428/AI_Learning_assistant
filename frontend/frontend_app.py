import sys
from pathlib import Path

# Ensure root directory is in sys.path when imported from root app.py
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
from frontend.ui.api_client import APIClient
from frontend.ui.components import inject_custom_css
from frontend.ui.learning_interface import render_learning_interface
from frontend.ui.quiz_interface import render_quiz_interface

# Streamlit Page Configuration
st.set_page_config(
    page_title="AI Learning Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


def render_home_hub():
    """Renders the main interactive landing page with mode selector cards."""
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0 1rem 0;">
        <h1 style="font-size: 2.6rem; font-weight: 800; background: linear-gradient(135deg, #2563eb, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
            🎓 AI Learning Assistant
        </h1>
        <p style="font-size: 1.15rem; color: #6b7280; max-width: 700px; margin: 0 auto 2rem auto;">
            Your autonomous university study companion. Grounded strictly in your lecture notes, slide decks, and past question papers.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🚀 Choose Your Study Mode")

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("### 🎓 Learning Mode")
            st.markdown("""
            - 💬 **Interactive Concept Q&A** with your lecture slides
            - 📑 **Exact Slide & Page Citations** with page numbers
            - 🧮 **LaTeX Equations & Algorithmic Tracing**
            - 🛡️ **Syllabus Boundary Safeguards**
            """)
            if st.button("Enter Learning Mode ➔", key="btn_enter_learning", type="primary", use_container_width=True):
                st.session_state.active_mode = "learning"
                st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown("### 🎯 Quiz Mode")
            st.markdown("""
            - 📝 **AI-Generated Multiple-Choice Quizzes**
            - ⚡ **Dynamic Difficulty Levels** (Easy, Medium, Hard)
            - 🔢 **Custom Question Counts** (3, 5, 10, 15)
            - 🏆 **Instant Scoring, Detailed Explanations & Hints**
            """)
            if st.button("Enter Quiz Mode ➔", key="btn_enter_quiz", type="primary", use_container_width=True):
                st.session_state.active_mode = "quiz"
                st.rerun()

    st.markdown("---")
    st.markdown("### 🔮 Upcoming Modes")
    c3, c4, c5 = st.columns(3)
    with c3:
        with st.container(border=True):
            st.markdown("#### 📋 Exam Mode")
            st.caption("Timed university mock tests and end-semester PYQ grading simulation.")
            st.info("Coming Soon")
    with c4:
        with st.container(border=True):
            st.markdown("#### 🧪 Lab Mode")
            st.caption("Practical coding experiment walkthroughs, test cases, and lab manual assistance.")
            st.info("Coming Soon")
    with c5:
        with st.container(border=True):
            st.markdown("#### ⚡ Revision Mode")
            st.caption("One-page high-yield formula cheat sheets and flashcard summaries.")
            st.info("Coming Soon")


def main():
    inject_custom_css()
    api_client = APIClient(base_url=None)

    # Initialize Active Mode State (defaults to 'home')
    if "active_mode" not in st.session_state:
        st.session_state.active_mode = "home"

    # Render Active Mode View
    if st.session_state.active_mode == "learning":
        render_learning_interface(api_client)
    elif st.session_state.active_mode == "quiz":
        render_quiz_interface(api_client)
    else:
        render_home_hub()


if __name__ == "__main__":
    main()
