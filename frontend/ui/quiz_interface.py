import logging
import streamlit as st

from frontend.ui.api_client import APIClient
from frontend.ui.sidebar import SidebarManager
from frontend.ui.components import (
    render_header,
    render_quiz_about,
    render_error,
    get_user_friendly_error_message,
)

logger = logging.getLogger(__name__)


def render_quiz_interface(api_client):
    """
    Renders the dedicated Interactive Quiz Studio.
    Controls (Subject, Difficulty, Question Count, and Generate Quiz button)
    are strictly housed in the sidebar. The central view displays the About section
    initially and dynamically switches to the active quiz questionnaire and grading sheet upon generation.
    """
    # 1. Render dedicated sidebar with all controls
    SidebarManager.render_quiz_sidebar(api_client)

    # 2. Render Header
    render_header(
        title="🎯 Interactive Quiz Studio",
        subtitle="Test your conceptual mastery with AI-generated multiple-choice questions grounded in course materials"
    )

    # 3. Initialize Session States for Quiz
    if "quiz_data" not in st.session_state:
        st.session_state.quiz_data = None
    if "quiz_evaluation" not in st.session_state:
        st.session_state.quiz_evaluation = None
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}

    # 4. If no quiz has been generated yet, display the About / Instructions Section
    if not st.session_state.quiz_data:
        render_quiz_about()
        return

    # 5. Render Active Quiz Sheet (Replaces About section)
    quiz = st.session_state.quiz_data
    questions = quiz.get("questions", [])
    displayed_topic = quiz.get("topic") or st.session_state.get("quiz_subject_select", "Selected Subject")

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
            label_visibility="collapsed",
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
    with col_sub2:
        reset_quiz = st.button("🔄 Reset Quiz", type="secondary", use_container_width=True)

    if reset_quiz:
        st.session_state.quiz_evaluation = None
        st.session_state.user_answers = {}
        for key in list(st.session_state.keys()):
            if key.startswith("opt_radio_"):
                st.session_state.pop(key, None)
        st.rerun()

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
                    user_answers=collected_answers,
                )
                st.session_state.quiz_evaluation = evaluation
                st.rerun()
            except Exception as exc:
                logger.error(f"Quiz evaluation failed: {exc}")
                render_error(get_user_friendly_error_message(exc))

    # 6. Render Results & Score Breakdown
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
