import streamlit as st

DEFAULT_SUBJECTS = [
    "AI",
    "Biology",
    "COA",
    "DAA",
    "DBMS",
    "DEC",
    "Discrete Maths",
    "MEE",
    "OOP Java",
    "Operating system",
    "Optimization Techniques",
    "Python",
]


def render_sidebar():
    """
    Renders a dedicated Learning Mode sidebar with navigation back to the Hub,
    course subject filters, tips, and session reset controls.
    """
    with st.sidebar:
        st.markdown("### 🎓 Learning Mode")
        st.caption("Lecture Notes & Slide Q&A Companion")

        # Back to Modes Hub Navigation Button
        if st.button("🏠 Back to Modes Hub", use_container_width=True, type="primary"):
            st.session_state.active_mode = "home"
            st.rerun()

        st.divider()

        st.markdown("#### 📚 Course Subject Filter")

        selected_subject = st.selectbox(
            "Select Subject:",
            options=DEFAULT_SUBJECTS,
            index=0,
            help="Select a subject to search specific course notes.",
            key="learning_subject_select",
        )

        st.session_state.selected_subject = selected_subject

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
