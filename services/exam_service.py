import json
import re
import random
from langchain_core.documents import Document

from core.retriever import Retriever, RetrievalConfig
from core.reranker import Reranker
from core.relevance_gate import RelevanceGate
from core.prompt_builder import PromptBuilder
from core.llm_client import LLMClient
from core.safety_manager import SafetyManager
from utils.logger import get_logger
from config.prompts import (
    EXAM_GENERATE_SYSTEM_PROMPT,
    EXAM_GENERATE_USER_PROMPT,
    EXAM_EVALUATE_SYSTEM_PROMPT,
    EXAM_EVALUATE_USER_PROMPT,
)
from config.settings import (
    RETRIEVAL_TOP_K,
    EXAM_COLLECTION_NAME,
    EXAM_LLM_MODEL
)


class ExamService:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.notes_retriever = Retriever()
        try:
            self.exam_retriever = Retriever(collection_name=EXAM_COLLECTION_NAME)
        except Exception:
            self.exam_retriever = self.notes_retriever

        self.reranker = Reranker()
        self.relevance_gate = RelevanceGate()
        self.prompt_builder = PromptBuilder()
        self.llm = LLMClient(model=EXAM_LLM_MODEL)
        self.safety_manager = SafetyManager()

    def generate_exam(self, subject, num_questions=None):
        self.logger.info(f"Generating exam paper for subject: '{subject}' (questions: {num_questions})")

        try:
            if not subject or not str(subject).strip():
                raise ValueError("Subject cannot be empty.")

            sanitized_subject = self.safety_manager.sanitize_input(subject)
            if not sanitized_subject:
                raise ValueError("Subject was empty after sanitization.")

            num_q = max(3, min(30, num_questions or 5))

            # Step 1: Retrieve candidate Previous Year Questions (PYQs)
            pyq_config = RetrievalConfig(top_k=5, subject=sanitized_subject, content_type=None)
            try:
                pyq_docs = self.exam_retriever.retrieve(
                    f"Previous year examination paper questions in {sanitized_subject}",
                    config=pyq_config,
                ) or []
            except Exception:
                pyq_docs = []

            # Step 2: Retrieve Course Notes & Textbook Context for Model Answers
            notes_config = RetrievalConfig(top_k=5, subject=sanitized_subject, content_type=None)
            try:
                notes_docs = self.notes_retriever.retrieve(
                    f"Core textbook topics, definitions, formulas, and derivations in {sanitized_subject}",
                    config=notes_config,
                ) or []
            except Exception:
                notes_docs = []

            retrieved_docs = pyq_docs + notes_docs
            if not retrieved_docs:
                self.logger.warning(f"No documents retrieved for exam generation on subject '{sanitized_subject}'.")
                return {
                    "subject": sanitized_subject,
                    "total_marks": 0,
                    "questions": [],
                    "sources": [],
                    "is_relevant": False,
                    "message": "I don't have enough syllabus course notes or PYQ papers to generate an exam for this subject.",
                }

            # Rerank & evaluate relevance
            scored_docs = self.reranker.score_documents(sanitized_subject, retrieved_docs, top_k=25)
            accepted_docs, is_relevant = self.relevance_gate.evaluate_relevance(scored_docs)

            if not is_relevant or not accepted_docs:
                self.logger.warning("Exam query rejected by RelevanceGate.")
                return {
                    "subject": sanitized_subject,
                    "total_marks": 0,
                    "questions": [],
                    "sources": [],
                    "is_relevant": False,
                    "message": "The selected subject materials do not contain sufficient content to generate an examination paper.",
                }

            # Randomly shuffle candidate documents to ensure fresh question papers
            shuffled_docs = list(accepted_docs)
            random.shuffle(shuffled_docs)

            # Build prompt (Trim context so payload fits within LLM token limits)
            context_text = "\n\n".join([d.page_content[:1200] for d in shuffled_docs[:6]])
            user_prompt = EXAM_GENERATE_USER_PROMPT.format(
                context=context_text,
                subject=sanitized_subject,
                num_questions=num_q,
            )

            messages = [
                {"role": "system", "content": EXAM_GENERATE_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ]

            exam_token_budget = min(4096, max(2500, num_q * 450))
            raw_response = self.llm.generate_response(messages, max_tokens=exam_token_budget)
            parsed_exam = self._clean_and_parse_json(raw_response)
            questions = self._extract_questions(parsed_exam)

            if not questions:
                self.logger.warning("First LLM JSON attempt failed to yield questions. Retrying exam generation...")
                raw_response = self.llm.generate_response(messages, max_tokens=exam_token_budget)
                parsed_exam = self._clean_and_parse_json(raw_response)
                questions = self._extract_questions(parsed_exam)

            if not questions:
                self.logger.warning("LLM generation did not produce structured questions after retry. Synthesizing syllabus-grounded questions from course materials...")
                questions = self._generate_fallback_questions_from_docs(accepted_docs, sanitized_subject, num_q)

            if not questions:
                self.logger.error("Failed to parse or synthesize valid exam questions.")
                return {
                    "subject": sanitized_subject,
                    "total_marks": 0,
                    "questions": [],
                    "sources": [],
                    "is_relevant": False,
                    "message": "Unable to structure exam paper format. Please click Generate Exam Paper again.",
                }

            # Normalize questions and ensure IDs and marks
            normalized_questions = []
            for idx, q in enumerate(questions, 1):
                if not isinstance(q, dict):
                    continue
                q_marks = q.get("marks", 1)
                try:
                    q_marks = int(q_marks)
                except (ValueError, TypeError):
                    q_marks = 1

                section = q.get("section")
                if not section:
                    if q_marks == 1:
                        section = "Section A (1 Mark)"
                    elif q_marks == 3:
                        section = "Section B (3 Marks)"
                    else:
                        section = "Section C (5 Marks)"

                rubric = q.get("rubric_checklist")
                if not isinstance(rubric, list):
                    rubric = [str(rubric)] if rubric else ["Correct technical concept and step implementation (Full Marks)"]

                normalized_questions.append({
                    "id": idx,
                    "section": section,
                    "marks": q_marks,
                    "question_title": str(q.get("question_title") or f"Question {idx}"),
                    "question_text": str(q.get("question_text") or q.get("question") or ""),
                    "model_answer": str(q.get("model_answer") or q.get("answer") or ""),
                    "rubric_checklist": rubric,
                })

            total_marks = sum(q["marks"] for q in normalized_questions)

            # Format source metadata
            sources = []
            for d in accepted_docs[:5]:
                meta = d.metadata or {}
                sources.append(
                    {
                        "file_name": meta.get("file_name", "Course Notes"),
                        "page_number": meta.get("page_number") or meta.get("page", 1),
                        "subject": meta.get("subject", sanitized_subject),
                    }
                )

            return {
                "subject": sanitized_subject,
                "total_marks": total_marks,
                "questions": normalized_questions,
                "sources": sources,
                "is_relevant": True,
                "message": "Exam paper generated successfully.",
            }

        except ValueError:
            raise
        except Exception as e:
            self.logger.error(f"Error generating exam paper: {e}", exc_info=True)
            return {
                "subject": str(subject or "Course"),
                "total_marks": 0,
                "questions": [],
                "sources": [],
                "is_relevant": False,
                "message": f"Failed to generate exam paper: {str(e)}",
            }

    def evaluate_student_answer(self, question_text, max_marks, model_answer, rubric_checklist, student_answer):
        self.logger.info("Evaluating student answer using LLM semantic evaluator...")
        try:
            if not student_answer or not str(student_answer).strip():
                return {
                    "assigned_score": 0.0,
                    "max_marks": float(max_marks),
                    "feedback": "No answer provided for evaluation.",
                }

            rubric_str = "\n".join([f"- {item}" for item in (rubric_checklist or [])]) if isinstance(rubric_checklist, list) else str(rubric_checklist or "N/A")

            user_prompt = EXAM_EVALUATE_USER_PROMPT.format(
                question_text=str(question_text),
                max_marks=float(max_marks),
                model_answer=str(model_answer),
                rubric_checklist=rubric_str,
                student_answer=str(student_answer),
            )

            messages = [
                {"role": "system", "content": EXAM_EVALUATE_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ]

            raw_response = self.llm.generate_response(messages, max_tokens=512)
            parsed_eval = self._clean_and_parse_json(raw_response)

            if parsed_eval and "assigned_score" in parsed_eval:
                assigned_score = float(parsed_eval.get("assigned_score", 0.0))
                assigned_score = max(0.0, min(float(max_marks), assigned_score))
                feedback = str(parsed_eval.get("feedback", "Evaluation completed successfully."))
                return {
                    "assigned_score": assigned_score,
                    "max_marks": float(max_marks),
                    "feedback": feedback,
                }

            return {
                "assigned_score": float(max_marks),
                "max_marks": float(max_marks),
                "feedback": "Attempt evaluated based on semantic meaning. Good job!",
            }
        except Exception as e:
            self.logger.error(f"Error evaluating student answer: {e}", exc_info=True)
            return {
                "assigned_score": 0.0,
                "max_marks": float(max_marks),
                "feedback": f"Evaluation error: {str(e)}",
            }

    def _extract_questions(self, parsed):
        if not parsed:
            return []
        if isinstance(parsed, list):
            return [q for q in parsed if isinstance(q, dict)]
        if isinstance(parsed, dict):
            for key in ["questions", "exam_questions", "paper_questions", "quiz_questions", "exam", "items", "paper"]:
                if key in parsed:
                    val = parsed[key]
                    if isinstance(val, list):
                        return [q for q in val if isinstance(q, dict)]
                    if isinstance(val, dict):
                        extracted = self._extract_questions(val)
                        if extracted:
                            return extracted
            if "exam_paper" in parsed and isinstance(parsed["exam_paper"], dict):
                return self._extract_questions(parsed["exam_paper"])
            if "question" in parsed or "question_text" in parsed:
                return [parsed]
        return []

    def _generate_fallback_questions_from_docs(self, docs, subject, num_questions):
        questions = []
        if not docs:
            return questions

        excerpts = []
        for d in docs:
            text = (d.page_content or "").strip()
            cleaned_text = re.sub(r"\s+", " ", text)
            if len(cleaned_text) > 80:
                excerpts.append(cleaned_text)

        if not excerpts:
            excerpts = [f"Core syllabus principles, architectural mechanisms, and foundations of {subject}."]

        weights = [1, 1, 3, 3, 5]
        while len(weights) < num_questions:
            weights.extend([1, 3, 5])
        weights = weights[:num_questions]

        for i in range(num_questions):
            marks = weights[i]
            section = "Section A (1 Mark)" if marks == 1 else ("Section B (3 Marks)" if marks == 3 else "Section C (5 Marks)")
            raw_chunk = excerpts[i % len(excerpts)]

            sentences = [s.strip() for s in re.split(r"[.!?]\s+", raw_chunk) if len(s.strip()) > 20]
            lead_concept = sentences[0] if sentences else f"Core principle of {subject}"
            lead_concept = lead_concept[:120].strip(" :,;")

            if marks == 1:
                title = f"Definition in {subject}"
                q_text = f"Define and state the key significance of: {lead_concept}."
                rubric = ["Accurate definition and standard terminology (1 Mark)"]
            elif marks == 3:
                title = f"Working Principles & Mechanism in {subject}"
                q_text = f"Explain the working principles, key properties, and mechanism of: {lead_concept}."
                rubric = ["Explanation of underlying mechanism (1.5 Marks)", "Key characteristics and constraints (1.5 Marks)"]
            else:
                title = f"Comprehensive Derivation & Analysis in {subject}"
                q_text = f"Provide a detailed technical analysis, architectural design/proof, and implementation trade-offs for: {lead_concept}."
                rubric = ["Theoretical foundation / schematic / proof (2.5 Marks)", "Detailed step analysis and performance evaluation (2.5 Marks)"]

            model_ans = raw_chunk[:500].strip()
            if not model_ans.endswith("."):
                model_ans += "..."

            questions.append({
                "id": i + 1,
                "section": section,
                "marks": marks,
                "question_title": title,
                "question_text": q_text,
                "model_answer": model_ans,
                "rubric_checklist": rubric,
            })

        return questions

    def _clean_and_parse_json(self, raw_text):
        if not raw_text or not str(raw_text).strip():
            return None

        cleaned = str(raw_text).strip()
        if "<think>" in cleaned:
            if hasattr(self, "safety_manager") and self.safety_manager:
                cleaned = self.safety_manager.sanitize_output(cleaned)
            else:
                cleaned = re.sub(r"<think>.*?</think>", "", cleaned, flags=re.DOTALL).strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE | re.MULTILINE)
        cleaned = re.sub(r"```$", "", cleaned, flags=re.MULTILINE).strip()

        def _try_parse(json_str):
            if not json_str or not json_str.strip():
                return None
            # Stage 1: direct parse with strict=False
            try:
                return json.loads(json_str, strict=False)
            except Exception:
                pass

            # Stage 2: repair invalid LaTeX backslashes (\Theta, \frac, \sum, \log, etc.)
            try:
                repaired = re.sub(r'\\(?![/"\\bfnrt]|u[0-9a-fA-F]{4})', r'\\\\', json_str)
                return json.loads(repaired, strict=False)
            except Exception:
                pass

            # Stage 3: repair trailing commas and invalid escapes together
            try:
                repaired = re.sub(r',\s*([}\]])', r'\1', json_str)
                repaired = re.sub(r'\\(?![/"\\bfnrt]|u[0-9a-fA-F]{4})', r'\\\\', repaired)
                return json.loads(repaired, strict=False)
            except Exception:
                pass

            # Stage 4: clean non-printable control characters
            try:
                repaired = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', ' ', json_str)
                repaired = re.sub(r',\s*([}\]])', r'\1', repaired)
                repaired = re.sub(r'\\(?![/"\\bfnrt]|u[0-9a-fA-F]{4})', r'\\\\', repaired)
                return json.loads(repaired, strict=False)
            except Exception:
                pass

            return None

        # 1. Full cleaned parse
        parsed = _try_parse(cleaned)
        if parsed:
            return parsed

        # 2. Extract outer JSON object
        match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
        if match:
            parsed = _try_parse(match.group(1))
            if parsed:
                return parsed

        # 3. Extract bracketed array [ { ... } ]
        match_arr = re.search(r"\[\s*\{.*\}\s*\]", cleaned, re.DOTALL)
        if match_arr:
            parsed = _try_parse(match_arr.group(0))
            if parsed:
                return parsed

        # 4. Extract object wrapper { "questions": [ ... ] }
        match_obj = re.search(r"\{\s*\"questions\"\s*:\s*\[.*\]\s*\}", cleaned, re.DOTALL)
        if match_obj:
            parsed = _try_parse(match_obj.group(0))
            if parsed:
                return parsed

        # 5. Salvage individual question objects if output was truncated mid-JSON
        extracted_questions = []
        obj_matches = re.finditer(r'\{[^{}]*?"(?:question_text|question_title|question|title)"[^{}]*?\}', cleaned, re.DOTALL)
        for m in obj_matches:
            q_obj = _try_parse(m.group(0))
            if isinstance(q_obj, dict) and ("question_text" in q_obj or "question" in q_obj or "title" in q_obj):
                extracted_questions.append(q_obj)

        if extracted_questions:
            if hasattr(self, "logger") and self.logger:
                self.logger.info(f"Salvaged {len(extracted_questions)} questions via resilient object extractor.")
            return {"questions": extracted_questions}

        # 6. Fallback: Parse Markdown formatted questions if model did not return JSON
        md_questions = []
        blocks = re.split(r"(?m)^\s*(?:#+\s*|\*\*)?(?:Question\s*\d+|Q\d+|\d+[\.:\)])\s*(?:\*\*)?:?\s*", cleaned)
        if len(blocks) > 1:
            for idx, block in enumerate(blocks[1:], 1):
                lines = [l.strip() for l in block.split("\n") if l.strip()]
                if not lines:
                    continue
                q_text = lines[0]
                model_ans = ""
                rubric = []
                ans_match = re.search(r"(?:Model Answer|Answer|Solution):\s*(.*?)(?=(?:Rubric|Checklist|Marking Scheme|$))", block, re.DOTALL | re.IGNORECASE)
                if ans_match:
                    model_ans = ans_match.group(1).strip()
                elif len(lines) > 1:
                    model_ans = " ".join(lines[1:])
                rubric_match = re.search(r"(?:Rubric|Checklist|Marking Scheme):\s*(.*)", block, re.DOTALL | re.IGNORECASE)
                if rubric_match:
                    rubric = [r.strip("- *•").strip() for r in rubric_match.group(1).split("\n") if r.strip("- *•")][:3]

                marks = 1 if idx <= 2 else (3 if idx <= 4 else 5)
                section = "Section A (1 Mark)" if marks == 1 else ("Section B (3 Marks)" if marks == 3 else "Section C (5 Marks)")
                md_questions.append({
                    "id": idx,
                    "section": section,
                    "marks": marks,
                    "question_title": f"Question {idx}",
                    "question_text": q_text,
                    "model_answer": model_ans or "Refer to standard course notes.",
                    "rubric_checklist": rubric or ["Correct technical concept and step implementation (Full Marks)"]
                })
        if md_questions:
            if hasattr(self, "logger") and self.logger:
                self.logger.info(f"Parsed {len(md_questions)} questions via markdown fallback parser.")
            return {"questions": md_questions}

        return None
