
import logging
import streamlit as st
from frontend.ui.components import render_header
from frontend.ui.sidebar import SidebarManager
logger = logging.getLogger(__name__)


@st.cache_resource
def get_exam_service():
    from services.exam_service import ExamService
    return ExamService()


def render_exam_interface(api_client):
    """
    Renders the Written Examination Hall Simulator interface.
    Supports physical paper solving, 1-Mark/3-Mark/5-Mark question papers,
    end-of-exam AI semantic batch evaluation, and detailed deduction explanations.
    """
    SidebarManager.render_exam_sidebar(api_client)

    render_header(
        title="📝 Exam Hall Simulator",
        subtitle="Syllabus-grounded written university assessment simulator with end-of-exam AI grading & deduction analysis"
    )

    # Initialize session state defaults
    if "exam_data" not in st.session_state:
        st.session_state.exam_data = None
    if "self_scores" not in st.session_state:
        st.session_state.self_scores = {}
    if "student_attempts" not in st.session_state:
        st.session_state.student_attempts = {}
    if "submitted_attempts" not in st.session_state:
        st.session_state.submitted_attempts = {}
    if "ai_feedback" not in st.session_state:
        st.session_state.ai_feedback = {}
    if "exam_finished" not in st.session_state:
        st.session_state.exam_finished = False

    exam_data = st.session_state.exam_data

    # State 1: No Exam Active -> Welcome Banner
    if not exam_data:
        st.markdown(
            """
            <div class="about-card" style="border-left: 5px solid #ec4899;">
                <h3>🏛️ Welcome to the University Examination Hall</h3>
                <p>
                    Simulate real engineering university exams with PYQs and syllabus-grounded question papers. 
                    Configure your subject and question count in the sidebar, then click <strong>🚀 Generate Exam Paper</strong> to begin.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                """
                <div style="background: rgba(59, 130, 246, 0.12); border-left: 4px solid #3b82f6; border-radius: 8px; padding: 1rem; min-height: 135px; margin-bottom: 1rem;">
                    <h5 style="margin: 0 0 0.5rem 0; color: #60a5fa; font-weight: 700;">⚖️ Standardized 1, 3 & 5-Mark Weightages</h5>
                    <p style="margin: 0; font-size: 0.9rem; color: #cbd5e1; line-height: 1.4;">
                        Questions categorized into Section A (1-Mark), Section B (3-Marks), and Section C (5-Marks).
                    </p>
                </div>
                <div style="background: rgba(16, 185, 129, 0.12); border-left: 4px solid #10b981; border-radius: 8px; padding: 1rem; min-height: 135px;">
                    <h5 style="margin: 0 0 0.5rem 0; color: #34d399; font-weight: 700;">✍️ Written Attempt Locking</h5>
                    <p style="margin: 0; font-size: 0.9rem; color: #cbd5e1; line-height: 1.4;">
                        Write and save your attempts for all questions under exam hall conditions without early solution reveals.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                """
                <div style="background: rgba(234, 179, 8, 0.12); border-left: 4px solid #eab308; border-radius: 8px; padding: 1rem; min-height: 135px; margin-bottom: 1rem;">
                    <h5 style="margin: 0 0 0.5rem 0; color: #fde047; font-weight: 700;">🤖 End-of-Exam AI Batch Grading</h5>
                    <p style="margin: 0; font-size: 0.9rem; color: #cbd5e1; line-height: 1.4;">
                        Submit the full paper at the end for automated semantic evaluation, question-wise scoring, and deduction notes.
                    </p>
                </div>
                <div style="background: rgba(236, 72, 153, 0.12); border-left: 4px solid #ec4899; border-radius: 8px; padding: 1rem; min-height: 135px;">
                    <h5 style="margin: 0 0 0.5rem 0; color: #f472b6; font-weight: 700;">📊 University O-E-A-B-C-D-U Scorecard</h5>
                    <p style="margin: 0; font-size: 0.9rem; color: #cbd5e1; line-height: 1.4;">
                        Automatic percentage calculation and 7-tier letter grade badges based on your university scale.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        return

    questions = exam_data.get("questions", [])
    num_q = len(questions)
    total_paper_marks = exam_data.get("total_marks", 20)
    subject = exam_data.get("subject", "Course")

    # Calculate Current Score
    current_self_score = sum(st.session_state.self_scores.get(str(q.get("id", idx + 1)), 0.0) for idx, q in enumerate(questions))
    pct = (current_self_score / total_paper_marks * 100) if total_paper_marks > 0 else 0.0

    # University Grade Calculation (O, E, A, B, C, D, U)
    if pct >= 90:
        grade = "O (Outstanding)"
        grade_color = "#10b981"
    elif pct >= 80:
        grade = "E (Excellent)"
        grade_color = "#3b82f6"
    elif pct >= 70:
        grade = "A (Very Good)"
        grade_color = "#6366f1"
    elif pct >= 60:
        grade = "B (Good)"
        grade_color = "#f59e0b"
    elif pct >= 50:
        grade = "C (Fair)"
        grade_color = "#d97706"
    elif pct >= 40:
        grade = "D (Pass)"
        grade_color = "#8b5cf6"
    else:
        grade = "U (Re-appear)"
        grade_color = "#ef4444"

    # Count attempted questions
    saved_count = sum(1 for q in questions if st.session_state.submitted_attempts.get(str(q.get("id", 0)), False))

    # Top Status Bar Metrics
    st.markdown(f"### 📄 {subject} Written Examination Paper")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Subject", subject)
    m2.metric("Questions", f"{num_q} Items")
    m3.metric("Total Paper Marks", f"{total_paper_marks} Marks")
    if st.session_state.exam_finished:
        m4.metric("Your Final Score", f"{current_self_score:.1f} / {total_paper_marks}", f"{pct:.1f}% ({grade.split()[0]})")
    else:
        m4.metric("Attempt Status", f"{saved_count} / {num_q} Saved", "In Progress")

    st.divider()

    # State 3: Exam Finished Summary & Detailed Review View
    if st.session_state.exam_finished:
        st.markdown("## 📊 Examination Performance Report")

        st.markdown(
            f"""
            <div style="background: rgba(15, 23, 42, 0.6); border: 2px solid {grade_color}; border-radius: 12px; padding: 1.2rem; text-align: center; margin-bottom: 1.5rem;">
                <span style="font-size: 1rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em;">Final Awarded Grade</span><br/>
                <span style="font-size: 2.4rem; font-weight: 800; color: {grade_color};">{grade}</span><br/>
                <span style="font-size: 1.2rem; color: #e2e8f0; font-weight: 600;">Total Score: {current_self_score:.1f} / {total_paper_marks} ({pct:.1f}%)</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### 📑 Section-by-Section Score Breakdown")

        # Group scores by mark section
        sec_scores = {"Section A (1 Mark)": [0.0, 0], "Section B (3 Marks)": [0.0, 0], "Section C (5 Marks)": [0.0, 0]}
        for idx, q in enumerate(questions):
            qid = str(q.get("id", idx + 1))
            sec = q.get("section", "Section B (3 Marks)")
            marks = float(q.get("marks", 3))
            score = float(st.session_state.self_scores.get(qid, 0.0))

            if sec not in sec_scores:
                sec_scores[sec] = [0.0, 0]
            sec_scores[sec][0] += score
            sec_scores[sec][1] += int(marks)

        col_sec1, col_sec2, col_sec3 = st.columns(3)
        cols = [col_sec1, col_sec2, col_sec3]
        for idx, (sec_name, (earned, max_m)) in enumerate(sec_scores.items()):
            if max_m > 0:
                sec_pct = (earned / max_m) * 100
                cols[idx % 3].metric(sec_name, f"{earned:.1f} / {max_m}", f"{sec_pct:.1f}%")

        st.divider()
        st.markdown("### 🔍 Question-by-Question AI Evaluation & Deduction Review")

        for idx, q in enumerate(questions):
            qid = str(q.get("id", idx + 1))
            sec_title = q.get("section", "Section B (3 Marks)")
            q_marks = int(q.get("marks", 3))
            q_title = q.get("question_title", f"Question {idx + 1}")
            q_text = q.get("question_text", "")
            model_ans = q.get("model_answer", "")
            rubric = q.get("rubric_checklist", [])
            saved_attempt = st.session_state.student_attempts.get(qid, "")
            awarded = float(st.session_state.self_scores.get(qid, 0.0))
            feedback = st.session_state.ai_feedback.get(qid, "")

            # Badge color
            if awarded == q_marks:
                score_badge_bg = "#10b981"  # green
            elif awarded > 0:
                score_badge_bg = "#f59e0b"  # amber
            else:
                score_badge_bg = "#ef4444"  # red

            with st.container(border=True):
                st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span style="font-weight: 700; font-size: 1.1rem; color: #f8fafc;">Q{idx + 1}. {q_title} ({sec_title})</span>
                        <span style="background: {score_badge_bg}; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.85rem; font-weight: 700;">
                            Awarded: {awarded:.1f} / {q_marks}.0 Marks
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown(f"**{q_text}**")
                st.divider()

                # Render AI Examiner Evaluation & Deduction Note
                st.markdown("**🤖 AI Examiner Evaluation & Deduction Analysis:**")
                if awarded < q_marks:
                    st.warning(f"**Score Awarded: {awarded:.1f} / {q_marks}.0 Marks**\n\n{feedback}")
                else:
                    st.success(f"**Score Awarded: {awarded:.1f} / {q_marks}.0 Marks (Full Marks)**\n\n{feedback}")

                col_left, col_right = st.columns(2)

                with col_left:
                    st.markdown("**📝 Your Submitted Attempt:**")
                    if saved_attempt:
                        st.info(saved_attempt)
                    else:
                        st.error("No answer submitted for this question.")

                with col_right:
                    st.markdown("**💡 Ground-Truth Reference Model Answer & Explanation:**")
                    st.info(model_ans)

                if rubric:
                    st.markdown("**📝 Marking Rubric Checklist:**")
                    for item in rubric:
                        st.markdown(f"- {item}")

        st.divider()

        if st.button("🔄 Take Another Examination", type="primary", use_container_width=True):
            st.session_state.exam_data = None
            st.session_state.self_scores = {}
            st.session_state.student_attempts = {}
            st.session_state.submitted_attempts = {}
            st.session_state.ai_feedback = {}
            st.session_state.exam_finished = False
            st.rerun()

        return

    # State 2: Interactive Question Paper Writing Phase (No Solution Reveal Until End)
    st.info("✍️ **Exam Hall Instructions**: Answer each question in the box below and click **🔒 Save Attempt**. When you have completed all questions, click **🏁 Finish & Submit Entire Examination Paper** at the bottom to trigger AI evaluation and view your detailed scorecard.")

    for idx, q in enumerate(questions):
        qid = str(q.get("id", idx + 1))
        sec_title = q.get("section", "Section B (3 Marks)")
        q_marks = int(q.get("marks", 3))
        q_title = q.get("question_title", f"Question {idx + 1}")
        q_text = q.get("question_text", "")

        # Color-coded section badge
        if q_marks == 1:
            badge_bg = "#10b981"  # green
        elif q_marks == 3:
            badge_bg = "#2563eb"  # blue
        else:
            badge_bg = "#ec4899"  # pink

        with st.container(border=True):
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="font-weight: 700; font-size: 1.1rem; color: #f8fafc;">Q{idx + 1}. {q_title}</span>
                    <span style="background: {badge_bg}; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.85rem; font-weight: 700;">
                        {sec_title} ({q_marks} {'Mark' if q_marks == 1 else 'Marks'})
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(f"**{q_text}**")

            st.divider()

            # Attempt Input & Save State
            is_saved = st.session_state.submitted_attempts.get(qid, False)
            saved_attempt = st.session_state.student_attempts.get(qid, "")

            attempt_text = st.text_area(
                f"✍️ Your Answer / Derivation / Key Steps for Q{idx + 1}:",
                value=saved_attempt,
                placeholder="Type your response here (or summary of your paper derivation)...",
                key=f"attempt_input_{qid}",
                height=120
            )

            col_save, col_status = st.columns([1.5, 3])
            with col_save:
                if st.button(f"🔒 Save Attempt Q{idx + 1}", key=f"save_btn_{qid}", type="primary", use_container_width=True):
                    if not attempt_text or not attempt_text.strip():
                        st.warning("⚠️ Please write an answer before saving!")
                    else:
                        st.session_state.student_attempts[qid] = attempt_text.strip()
                        st.session_state.submitted_attempts[qid] = True
                        st.rerun()
            with col_status:
                if is_saved:
                    st.success("✅ **Attempt Saved & Locked for Final Evaluation**")
                else:
                    st.caption("ℹ️ *Click Save Attempt when ready. Solutions & scores will be revealed after final paper submission.*")

    st.divider()

    # Final Exam Submission Button
    if st.button("🏁 Finish & Submit Entire Examination Paper", type="primary", use_container_width=True):
        exam_service = get_exam_service()
        with st.spinner("🤖 AI Examiner is evaluating your complete examination paper..."):
            for idx, q in enumerate(questions):
                qid = str(q.get("id", idx + 1))
                q_marks = int(q.get("marks", 3))
                q_text = q.get("question_text", "")
                model_ans = q.get("model_answer", "")
                rubric = q.get("rubric_checklist", [])
                student_text = st.session_state.student_attempts.get(qid, "")

                if student_text and student_text.strip():
                    eval_res = exam_service.evaluate_student_answer(
                        question_text=q_text,
                        max_marks=q_marks,
                        model_answer=model_ans,
                        rubric_checklist=rubric,
                        student_answer=student_text.strip()
                    )
                else:
                    eval_res = {
                        "assigned_score": 0.0,
                        "max_marks": float(q_marks),
                        "feedback": "Question was left unattempted. No marks awarded."
                    }

                st.session_state.self_scores[qid] = float(eval_res.get("assigned_score", 0.0))
                st.session_state.ai_feedback[qid] = str(eval_res.get("feedback", ""))

        st.session_state.exam_finished = True
        st.rerun()
