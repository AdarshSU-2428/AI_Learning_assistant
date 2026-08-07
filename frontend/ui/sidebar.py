import streamlit as st


def render_sidebar():
    """
    Renders a polished, student-focused sidebar with application branding,
    usage instructions, and session control actions.
    """
    with st.sidebar:
        st.markdown("### 🎓 AI Learning Assistant")
        st.caption("Student Study Companion v1.0")

        st.divider()

        st.markdown("#### 📚 Course Subject Filter")
        try:
            from core.vector_store import VectorStore
            db_subjects = VectorStore().get_all_subjects()
        except Exception:
            db_subjects = []

        subjects = ["All Subjects"] + (db_subjects if db_subjects else [
            "DBMS", "DAA", "AI", "Discrete Maths", "Optimization Techniques", "Operating system", "Python", "COA", "DEC", "Biology", "MEE"
        ])

        selected_subject = st.selectbox(
            "Select Subject:",
            options=subjects,
            index=0,
            help="Select a subject to search specific course notes, or 'All Subjects' for global search.",
        )

        st.session_state.selected_subject = (
            None if selected_subject == "All Subjects" else selected_subject
        )

        st.divider()

        st.markdown("#### 📖 About")
        st.write(
            "The AI Learning Assistant is your dedicated study tool. "
            "Ask questions about course topics, request concept summaries, "
            "or explore detailed document references to support your learning."
        )

        st.divider()

        st.markdown("#### 💡 Quick Tips")
        st.markdown(
            "- **Be Specific:** Ask targeted questions about key topics or assignments.\n"
            "- **Check Sources:** Expand the *Sources & References* section below answers for deeper study.\n"
            "- **Clear & Reset:** Start a new study session anytime using the button below."
        )

        st.divider()

        if st.button("🧹 Clear Conversation", use_container_width=True, type="secondary"):
            st.session_state.messages = []
            st.rerun()
