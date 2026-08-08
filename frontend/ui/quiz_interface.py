import logging
import streamlit as st

from frontend.ui.api_client import APIClient
from frontend.ui.components import (
    render_header,
    render_error,
    get_user_friendly_error_message,
)

logger = logging.getLogger(__name__)

# Standard indexed subjects for fast, decoupled frontend selection
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


def render_quiz_interface(api_client):
    """
    Renders the dedicated Interactive Quiz Studio with subject dropdowns,
    difficulty selectors, question count slider up to 30, instant submission scoring, and hints.
    """
    render_header()

    st.markdown("## 🎯 Interactive Quiz Studio")
    st.caption("Test your conceptual mastery with AI-generated multiple-choice questions grounded in your course materials.")

    # Initialize Session States for Quiz
    if "quiz_data" not in st.session_state:
        st.session_state.quiz_data = None
    if "quiz_evaluation" not in st.session_state:
        st.session_state.quiz_evaluation = None
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}

    # 1. Configuration Panel
    with st.container():
        st.markdown("### ⚙️ Quiz Settings")
        col1, col2, col3 = st.columns(3)

        with col1:
            selected_subject = st.selectbox(
                "Select Subject",
                options=DEFAULT_SUBJECTS,
                index=0,
                key="quiz_subject_select"
            )

        with col2:
            difficulty = st.selectbox(
                "Difficulty Level",
                options=["Standard", "Easy", "Medium", "Hard"],
                index=0,
                key="quiz_difficulty_select"
            )

        with col3:
            num_questions = st.select_slider(
                "Number of Questions",
                options=[3, 5, 10, 15, 20, 25, 30],
                value=5,
                key="quiz_num_q_select"
            )

        generate_btn = st.button("🚀 Generate Quiz", type="primary", use_container_width=True)

        if generate_btn:
            with st.spinner(f"Generating {num_questions} questions for '{selected_subject}'..."):
                try:
                    diff_arg = None if difficulty == "Standard" else difficulty
                    quiz_res = api_client.generate_quiz(
                        topic=selected_subject,
                        subject=selected_subject,
                        num_questions=num_questions,
                        difficulty=diff_arg
                    )

                    if not quiz_res.get("is_relevant", True) or not quiz_res.get("questions"):
                        st.warning(quiz_res.get("message", "No questions could be generated for this subject."))
                        st.session_state.quiz_data = None
                        st.session_state.quiz_evaluation = None
                        return

                    st.session_state.quiz_data = quiz_res
                    st.session_state.quiz_evaluation = None
                    st.session_state.user_answers = {}
                    st.rerun()

                except Exception as exc:
                    logger.error(f"Quiz generation failed: {exc}")
                    render_error(get_user_friendly_error_message(exc))

    # 2. Render Active Quiz Sheet
    if st.session_state.quiz_data and st.session_state.quiz_data.get("questions"):
        quiz = st.session_state.quiz_data
        questions = quiz["questions"]
        displayed_topic = quiz.get("topic") or selected_subject

        st.markdown("---")
        st.markdown(f"### 📝 Practice Questions for **{displayed_topic}** ({len(questions)} Questions)")

        for idx, q in enumerate(questions, start=1):
            q_id = q.get("id", idx)
            st.markdown(f"#### **Q{idx}. {q.get('question')}**")

            options = q.get("options", [])
            selected_opt = st.radio(
                f"Choose your option for Question {idx}:",
                options=options,
                index=None,
                key=f"opt_radio_{q_id}",
                label_visibility="collapsed"
            )

            # Store selected letter (e.g. 'A', 'B', 'C', 'D')
            if selected_opt:
                letter = selected_opt.split(")")[0].strip().upper()
                st.session_state.user_answers[q_id] = letter

            # Collapsible Hint
            if q.get("hint"):
                with st.expander("💡 Need a Hint?"):
                    st.info(q.get("hint"))

            st.write("")

        col_sub1, col_sub2 = st.columns([2, 1])
        with col_sub1:
            submit_quiz = st.button("✅ Submit Answers", type="primary", use_container_width=True)

        if submit_quiz:
            with st.spinner("Grading your submission..."):
                try:
                    collected_answers = {}
                    for idx, q in enumerate(questions, start=1):
                        q_id = q.get("id", idx)
                        selected_val = st.session_state.get(f"opt_radio_{q_id}")
                        if selected_val:
                            letter = selected_val.split(")")[0].strip().upper()
                            collected_answers[str(q_id)] = letter
                            collected_answers[q_id] = letter

                    st.session_state.user_answers = collected_answers

                    evaluation = api_client.evaluate_quiz(
                        quiz_questions=questions,
                        user_answers=collected_answers
                    )
                    st.session_state.quiz_evaluation = evaluation
                    st.rerun()
                except Exception as exc:
                    logger.error(f"Quiz evaluation failed: {exc}")
                    render_error(get_user_friendly_error_message(exc))

    # 3. Render Results & Citations
    if st.session_state.quiz_evaluation:
        eval_res = st.session_state.quiz_evaluation
        score = eval_res.get("score", 0)
        total = eval_res.get("total", 0)
        percentage = eval_res.get("percentage", 0.0)

        st.markdown("---")
        st.markdown("### 🏆 Quiz Results & Score Breakdown")

        if percentage >= 80:
            st.success(f"🎉 **Outstanding Job! Score: {percentage}% ({score} / {total} Correct)**")
        elif percentage >= 50:
            st.info(f"👍 **Good Effort! Score: {percentage}% ({score} / {total} Correct)**")
        else:
            st.warning(f"📚 **Keep Practicing! Score: {percentage}% ({score} / {total} Correct)**")

        for d in eval_res.get("details", []):
            is_corr = d.get("is_correct", False)
            icon = "🟢" if is_corr else "🔴"
            status_text = "Correct" if is_corr else "Incorrect"

            with st.container():
                st.markdown(f"{icon} **Question {d.get('id')}: {status_text}**")
                st.markdown(f"*{d.get('question')}*")
                st.write(f"- **Your Choice**: `{d.get('user_answer') or 'Unanswered'}`")
                st.write(f"- **Correct Answer**: `{d.get('correct_answer')}`")
                if d.get("explanation"):
                    st.info(f"📖 **Explanation**: {d.get('explanation')}")
                st.write("")

        # Source Citations
        if st.session_state.quiz_data and st.session_state.quiz_data.get("sources"):
            st.markdown("#### 📚 Slide Citations & Lecture References")
            for src in st.session_state.quiz_data["sources"]:
                page_info = f" (Slide {src.get('page_number')})" if src.get("page_number") else ""
                st.caption(f"📄 **{src.get('file_name')}**{page_info}")

        if st.button("🔄 Take Another Quiz", use_container_width=True):
            st.session_state.quiz_data = None
            st.session_state.quiz_evaluation = None
            st.session_state.user_answers = {}
            st.rerun()
