import logging
import streamlit as st

logger = logging.getLogger(__name__)

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

LAB_SUBJECTS = [
    "COA",
    "DAA",
    "DBMS",
    "DEC",
    "IWT",
    "OOP Java",
    "OS",
    "Python",
]


class SidebarManager:
    """
    Central manager for rendering mode-specific sidebars.
    Ensures all dropdowns, configuration controls, and mode navigation
    live strictly in the sidebar.
    """

    @staticmethod
    def render_home_sidebar():
        """Renders the sidebar for the main Home / Hub landing page."""
        with st.sidebar:
            st.markdown("### 🎓 AI Learning Assistant")
            st.caption("Select your desired study mode to begin")

            st.divider()

            st.markdown("#### 🚀 Jump to Mode")
            if st.button("🎓 Learning Mode", use_container_width=True, type="secondary"):
                st.session_state.active_mode = "learning"
                st.rerun()

            if st.button("🎯 Quiz Mode", use_container_width=True, type="secondary"):
                st.session_state.active_mode = "quiz"
                st.rerun()

            if st.button("🧪 Lab Mode", use_container_width=True, type="secondary"):
                st.session_state.active_mode = "lab"
                st.rerun()

            st.divider()

            st.markdown("#### 📊 Knowledge Base Status")
            st.markdown(
                """
                - 📚 **Learning Registry:** `Active`
                - 🎯 **Quiz Question Bank:** `6,000+ Items`
                - 🧪 **Lab Manuals & Code:** `Indexed`
                - 🛡️ **Grounding Filter:** `Enforced`
                """
            )

    @staticmethod
    def render_learning_sidebar():
        """Renders the sidebar for Learning Mode."""
        with st.sidebar:
            st.markdown("### 🎓 Learning Mode")
            st.caption("Lecture Notes & Slide Q&A")

            if st.button("🏠 Back to Modes Hub", use_container_width=True, type="primary"):
                st.session_state.active_mode = "home"
                st.rerun()

            st.divider()

            st.markdown("#### 📚 Course Subject")
            selected_subject = st.selectbox(
                "Select Subject:",
                options=DEFAULT_SUBJECTS,
                index=0,
                help="Filter concept retrieval to specific course notes.",
                key="learning_subject_select",
            )
            st.session_state.selected_subject = selected_subject

            st.divider()

            st.markdown("#### 💡 Quick Tips")
            st.markdown(
                "- **Specific Questions:** Ask for definitions, differences, or step-by-step algorithms.\n"
                "- **Page Citations:** Check the *Sources & References* tab for exact slides.\n"
                "- **Reset:** Start a fresh chat anytime using the button below."
            )

            st.divider()

            if st.button("🧹 Clear Conversation", use_container_width=True, type="secondary"):
                st.session_state.messages = []
                st.rerun()

    @staticmethod
    def render_quiz_sidebar(api_client):
        """Renders the sidebar for Quiz Mode with all configuration dropdowns and action triggers."""
        with st.sidebar:
            st.markdown("### 🎯 Quiz Mode")
            st.caption("Interactive Syllabus MCQ Studio")

            if st.button("🏠 Back to Modes Hub", use_container_width=True, type="primary"):
                st.session_state.active_mode = "home"
                st.rerun()

            st.divider()

            st.markdown("#### ⚙️ Quiz Configuration")

            # 1. Subject selector (Strict theory subjects without Lab defaults)
            selected_subject = st.selectbox(
                "Subject:",
                options=DEFAULT_SUBJECTS,
                index=0,
                help="Select the university course subject for your quiz.",
                key="quiz_sidebar_subject",
            )

            # 2. Difficulty selector
            selected_difficulty = st.selectbox(
                "Difficulty Level:",
                options=["Easy", "Medium", "Hard"],
                index=1,
                help="Easy: Definitions & basics | Medium: Conceptual & analytical | Hard: Edge-cases & derivations",
                key="quiz_sidebar_difficulty",
            )

            # 3. Question count slider
            selected_num_questions = st.slider(
                "Number of Questions:",
                min_value=3,
                max_value=30,
                value=5,
                step=1,
                help="Select between 3 and 30 questions per quiz session.",
                key="quiz_sidebar_num_questions",
            )

            st.divider()

            # 4. Generate Quiz Trigger Button
            if st.button("🚀 Generate Quiz", type="primary", use_container_width=True):
                with st.spinner(f"Generating {selected_num_questions} {selected_difficulty} MCQs for {selected_subject}..."):
                    try:
                        quiz_data = api_client.generate_quiz(
                            topic=selected_subject,
                            difficulty=selected_difficulty,
                            num_questions=selected_num_questions,
                            subject=selected_subject,
                        )

                        if quiz_data and "questions" in quiz_data and quiz_data["questions"]:
                            st.session_state.quiz_data = quiz_data
                            st.session_state.user_answers = {}
                            st.session_state.submitted = False
                            st.session_state.quiz_score = 0
                            st.session_state.show_hints = {}
                            st.rerun()
                        else:
                            st.error("No questions were generated. Please try again.")

                    except Exception as exc:
                        logger.error("Quiz generation failed: %s", exc, exc_info=True)
                        st.error(f"Failed to generate quiz: {exc}")

            if "quiz_data" in st.session_state and st.session_state.quiz_data:
                st.divider()
                if st.button("🔄 Reset Quiz Session", use_container_width=True, type="secondary"):
                    st.session_state.quiz_data = None
                    st.session_state.user_answers = {}
                    st.session_state.submitted = False
                    st.session_state.quiz_score = 0
                    st.session_state.show_hints = {}
                    st.rerun()

    @staticmethod
    def render_lab_sidebar():
        """Renders the sidebar for Practical Lab Mode."""
        with st.sidebar:
            st.markdown("### 🧪 Lab Mode")
            st.caption("Practical Experiments & Code Companion")

            if st.button("🏠 Back to Modes Hub", use_container_width=True, type="primary"):
                st.session_state.active_mode = "home"
                st.rerun()

            st.divider()

            st.markdown("#### 🔬 Lab Subject")
            selected_lab_subject = st.selectbox(
                "Select Lab Subject:",
                options=LAB_SUBJECTS,
                index=0,
                help="Select your laboratory course to retrieve experiment manuals and code assignments.",
                key="lab_subject_select",
            )
            st.session_state.selected_lab_subject = selected_lab_subject

            st.divider()

            st.markdown("#### 💡 Lab Features")
            st.markdown(
                "- 💻 **Runnable Programs:** Code with test cases & complexity.\n"
                "- ⚡ **Hardware/Circuits:** Pinouts, truth tables & diagrams.\n"
                "- 📊 **Observations:** Data tables & error percentages.\n"
                "- 🗣️ **Viva Prep:** Oral questions with model answers."
            )

            st.divider()

            if st.button("🧹 Clear Lab Chat", use_container_width=True, type="secondary"):
                st.session_state.lab_messages = []
                st.rerun()


# Legacy helper function for backward compatibility
def render_sidebar():
    SidebarManager.render_learning_sidebar()
