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
from core.vector_store import VectorStore
from config.prompts import QUIZ_SYSTEM_PROMPT, QUIZ_USER_PROMPT
from config.settings import (
    RETRIEVAL_TOP_K, 
    QUIZ_MAX_TOKENS, 
    QUIZ_COLLECTION_NAME,
    QUIZ_LLM_MODEL
)

class QuizService:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.retriever = Retriever()
        self.quiz_store = VectorStore(collection_name=QUIZ_COLLECTION_NAME)
        self.reranker = Reranker()
        self.relevance_gate = RelevanceGate()
        self.prompt_builder = PromptBuilder()
        self.llm = LLMClient(model=QUIZ_LLM_MODEL)
        self.safety_manager = SafetyManager()

    def generate_quiz(self, topic, subject=None, num_questions=None, difficulty=None):
        self.logger.info(f"Generating quiz for topic: '{topic}' (subject: {subject}, questions: {num_questions}, difficulty: {difficulty})")

        try:
            if not topic or not str(topic).strip():
                raise ValueError("Topic cannot be empty.")

            sanitized_topic = self.safety_manager.sanitize_input(topic)
            if not sanitized_topic:
                raise ValueError("Topic was empty after sanitization.")

            target_subject = subject or sanitized_topic
            num_q = num_questions if num_questions is not None else 5
            diff_val = difficulty if difficulty is not None else "Standard"

            # Phase 1: Try instant retrieval from curated quiz_bank collection
            bank_questions = self._get_curated_quiz_questions(
                subject=target_subject,
                difficulty=diff_val,
                num_questions=num_q
            )
            if bank_questions and len(bank_questions) >= num_q:
                self.logger.info(f"Returning {num_q} curated questions from quiz_bank collection.")
                sources = self._get_subject_sources(target_subject)
                return {
                    "topic": sanitized_topic,
                    "difficulty": difficulty,
                    "questions": bank_questions[:num_q],
                    "sources": sources,
                    "is_relevant": True,
                    "message": "Quiz loaded from verified question bank."
                }

            # Phase 2: Dynamic syllabus-grounded generation from lecture notes
            is_subject_level_quiz = (
                subject is not None
                and (
                    sanitized_topic.strip().lower() == subject.strip().lower()
                    or sanitized_topic.strip().lower() in ["all", "general", "full syllabus", "overall", "quiz"]
                )
            )

            accepted_docs = []

            # If generating a quiz for the whole subject, pull all subject chunks from ChromaDB for comprehensive syllabus coverage
            if is_subject_level_quiz:
                config = RetrievalConfig(subject=subject)
                where_filter = config.get_where_filter()
                try:
                    chroma_res = self.retriever.vector_store.collection.get(
                        where=where_filter,
                        include=["documents", "metadatas"]
                    )
                    texts = chroma_res.get("documents", [])
                    metas = chroma_res.get("metadatas", [])
                    for text, meta in zip(texts, metas):
                        if text and text.strip():
                            accepted_docs.append(Document(page_content=text, metadata=meta or {}))
                except Exception as fetch_err:
                    self.logger.warning(f"Direct subject fetch failed, falling back to retriever: {fetch_err}")

            # Fall back to vector retrieval + reranking if not subject-level or if direct fetch returned empty
            if not accepted_docs:
                search_query = sanitized_topic
                config = RetrievalConfig(top_k=RETRIEVAL_TOP_K, subject=subject, content_type=None)
                retrieved_docs = self.retriever.retrieve(search_query, config=config)

                if not retrieved_docs:
                    self.logger.warning("No documents found for quiz generation.")
                    return {
                        "topic": sanitized_topic,
                        "questions": [],
                        "sources": [],
                        "is_relevant": False,
                        "message": "No relevant course materials found for this topic to generate a quiz."
                    }

                scored_docs = self.reranker.score_documents(search_query, retrieved_docs, top_k=30)
                
                if subject:
                    accepted_docs = [doc for doc, _ in scored_docs if doc is not None][:12]
                    is_relevant = bool(accepted_docs)
                else:
                    accepted_docs, is_relevant = self.relevance_gate.evaluate_relevance(scored_docs)

                if not is_relevant or not accepted_docs:
                    self.logger.warning("Quiz topic rejected by RelevanceGate (out of syllabus).")
                    return {
                        "topic": sanitized_topic,
                        "questions": [],
                        "sources": [],
                        "is_relevant": False,
                        "message": "The requested topic is not covered in your uploaded course materials."
                    }

            num_q = num_questions if num_questions is not None else 5
            diff_val = difficulty if difficulty is not None else "Standard"

            # Dynamic token budget calibrated to question count (guarantees full generation without truncation)
            quiz_token_budget = min(4096, max(2048, num_q * 400))

            # Determine sample size based on question count to cover broad topics without exceeding context limits
            target_chunks = min(12, max(6, num_q + 2))

            if len(accepted_docs) > target_chunks:
                # Divide all accepted docs evenly into chronological/syllabus bins
                bin_size = len(accepted_docs) / target_chunks
                diversified_docs = []
                for i in range(target_chunks):
                    start_idx = int(i * bin_size)
                    end_idx = int((i + 1) * bin_size)
                    bin_slice = accepted_docs[start_idx:end_idx]
                    if bin_slice:
                        diversified_docs.append(random.choice(bin_slice))
                # Shuffle the sampled bins to prevent predictable linear question ordering
                random.shuffle(diversified_docs)
            else:
                diversified_docs = list(accepted_docs)
                random.shuffle(diversified_docs)

            context = self.prompt_builder.context_builder.build_context(diversified_docs)

            user_content = QUIZ_USER_PROMPT.format(
                context=context,
                topic=sanitized_topic,
                difficulty=diff_val,
                num_questions=num_q
            )

            messages = [
                {"role": "system", "content": QUIZ_SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ]

            raw_response = self.llm.generate_response(messages, max_tokens=quiz_token_budget)
            sanitized_response = self.safety_manager.sanitize_output(raw_response)

            questions = self._parse_quiz_json(sanitized_response)

            # Pad questions with bank_questions if generated count is less than requested num_q
            if bank_questions and len(questions) < num_q:
                existing_texts = {q.get("question", "").strip().lower() for q in questions}
                for bq in bank_questions:
                    if len(questions) >= num_q:
                        break
                    bq_text = bq.get("question", "").strip().lower()
                    if bq_text and bq_text not in existing_texts:
                        questions.append(bq)
                        existing_texts.add(bq_text)

            # Re-index sequential question IDs
            for idx, q in enumerate(questions, 1):
                q["id"] = idx

            # Extract slide and lecture citations specifically from the sampled diversified context
            sources = []
            seen_sources = set()
            for doc in diversified_docs:
                file_name = doc.metadata.get("file_name", "Unknown")
                page = doc.metadata.get("page_number")
                key = (file_name, page)
                if key not in seen_sources:
                    seen_sources.add(key)
                    sources.append({"file_name": file_name, "page_number": page})

            return {
                "topic": sanitized_topic,
                "difficulty": difficulty,
                "questions": questions,
                "sources": sources,
                "is_relevant": True,
                "message": "Quiz generated successfully."
            }

        except Exception as e:
            self.logger.error(f"Quiz generation error: {str(e)}")
            raise e

    def _parse_quiz_json(self, response_text):
        if not response_text or not str(response_text).strip():
            return []

        cleaned = str(response_text).strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned).strip()

        def _try_parse(json_str):
            if not json_str or not json_str.strip():
                return None
            # Stage 1: direct parse with strict=False
            try:
                return json.loads(json_str, strict=False)
            except Exception:
                pass

            # Stage 2: repair invalid LaTeX backslashes (\tau, \frac, \Delta, etc.)
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

            return None

        # 1. Full cleaned parse
        parsed = _try_parse(cleaned)
        if isinstance(parsed, list) and len(parsed) > 0:
            return parsed
        if isinstance(parsed, dict) and "questions" in parsed and isinstance(parsed["questions"], list):
            return parsed["questions"]
        if isinstance(parsed, dict) and "question" in parsed:
            return [parsed]

        # 2. Extract bracketed array [ { ... } ]
        match_arr = re.search(r"\[\s*\{.*\}\s*\]", cleaned, re.DOTALL)
        if match_arr:
            parsed = _try_parse(match_arr.group(0))
            if isinstance(parsed, list) and len(parsed) > 0:
                return parsed

        # 3. Extract object wrapper { "questions": [ ... ] }
        match_obj = re.search(r"\{\s*\"questions\"\s*:\s*\[.*\]\s*\}", cleaned, re.DOTALL)
        if match_obj:
            parsed = _try_parse(match_obj.group(0))
            if isinstance(parsed, dict) and "questions" in parsed:
                return parsed["questions"]

        # 4. Salvage individual question objects if output was truncated mid-JSON
        extracted_questions = []
        obj_matches = re.finditer(r'\{[^{}]*?"id"[^{}]*?"question"[^{}]*?"options"[^{}]*?\}', cleaned, re.DOTALL)
        for m in obj_matches:
            q_obj = _try_parse(m.group(0))
            if isinstance(q_obj, dict) and "question" in q_obj:
                extracted_questions.append(q_obj)

        if extracted_questions:
            self.logger.info(f"Salvaged {len(extracted_questions)} questions via resilient object extractor.")
            return extracted_questions

        # 5. Fallback: Parse non-JSON markdown formatted quiz questions (e.g. "Q1. ... A) ... B) ...")
        md_questions = []
        blocks = re.split(r"(?m)^\s*(?:Q?\d+[\.\)]|\*\*Q?\d+[\.\)]\*\*)\s*", cleaned)
        for idx, block in enumerate(blocks[1:], 1):
            lines = [l.strip() for l in block.split("\n") if l.strip()]
            if not lines:
                continue
            q_text = re.sub(r"(?is)^\s*(?:\*\*)?(?:Draft Questions|Mental Refinement|Self-Check|Thinking Process|Analysis|Step \d+):?\s*(?:\*\*)?\s*", "", lines[0]).strip()
            if not q_text and len(lines) > 1:
                q_text = lines[1]

            options = []
            correct_ans = "A"
            hint = ""
            explanation = ""
            for l in lines[1:]:
                opt_m = re.match(r"^(?:[A-D][\.\)]|\*\*[A-D][\.\)]\*\*)\s*(.*)", l)
                if opt_m:
                    options.append(opt_m.group(1).strip())
                elif "correct" in l.lower() or "answer:" in l.lower():
                    ans_m = re.search(r"\b([A-D])\b", l.upper())
                    if ans_m:
                        correct_ans = ans_m.group(1)
                elif "hint:" in l.lower():
                    hint = l.split(":", 1)[-1].strip()
                elif "explanation:" in l.lower():
                    explanation = l.split(":", 1)[-1].strip()

            if q_text and len(options) >= 2:
                md_questions.append({
                    "id": idx,
                    "question": q_text,
                    "options": options[:4],
                    "correct_answer": correct_ans,
                    "hint": hint,
                    "explanation": explanation
                })

        if md_questions:
            self.logger.info(f"Parsed {len(md_questions)} questions via markdown fallback parser.")
            return md_questions

        self.logger.warning(f"Could not parse quiz JSON from response. Response snippet: {cleaned[:300]}")
        return []

    def evaluate_submission(self, quiz_questions, user_answers):
        total = len(quiz_questions)
        if total == 0:
            return {"score": 0, "total": 0, "percentage": 0.0, "details": []}

        correct_count = 0
        details = []

        for quiz in quiz_questions:
            quiz_id = quiz.get("id")
            correct = str(quiz.get("correct_answer", "")).strip().upper()
            
            # Robust lookup supporting both integer and string keys
            raw_user_ans = (
                user_answers.get(quiz_id)
                if quiz_id in user_answers
                else user_answers.get(str(quiz_id), "")
            )
            user_ans = str(raw_user_ans or "").strip().upper()

            is_correct = (user_ans == correct) and bool(user_ans)
            if is_correct:
                correct_count += 1

            details.append({
                "id": quiz_id,
                "question": quiz.get("question"),
                "user_answer": user_ans if user_ans else "Unanswered",
                "correct_answer": correct,
                "is_correct": is_correct,
                "explanation": quiz.get("explanation"),
                "hint": quiz.get("hint")
            })

        percentage = round((correct_count / total) * 100, 2)

        return {
            "score": correct_count,
            "total": total,
            "percentage": percentage,
            "details": details
        }

    def _get_curated_quiz_questions(self, subject=None, difficulty=None, num_questions=None):
        try:
            filters = []
            if subject:
                filters.append({"subject": {"$eq": subject}})
            if difficulty and difficulty != "Standard":
                filters.append({"difficulty": {"$eq": difficulty}})

            if len(filters) == 1:
                where_filter = filters[0]
            elif len(filters) > 1:
                where_filter = {"$and": filters}
            else:
                where_filter = None

            res = self.quiz_store.collection.get(
                where=where_filter,
                include=["documents", "metadatas"]
            )
            metas = res.get("metadatas", [])
            if not metas and subject and difficulty and difficulty != "Standard":
                res = self.quiz_store.collection.get(
                    where={"subject": {"$eq": subject}},
                    include=["documents", "metadatas"]
                )
                metas = res.get("metadatas", [])

            if not metas:
                return []

            questions = []
            for idx, meta in enumerate(metas, 1):
                if not isinstance(meta, dict):
                    continue
                opts = meta.get("options", "[]")
                if isinstance(opts, str):
                    try:
                        opts = json.loads(opts)
                    except Exception:
                        opts = []

                # Skip raw un-parsed chunks that lack valid options or structured question text
                if not isinstance(opts, list) or len(opts) < 2:
                    continue

                q_text = meta.get("question", "").strip()
                if not q_text or len(q_text) < 10:
                    continue

                questions.append({
                    "id": len(questions) + 1,
                    "question": q_text,
                    "options": opts,
                    "correct_answer": meta.get("correct_answer", "A"),
                    "hint": meta.get("hint", ""),
                    "explanation": meta.get("explanation", "")
                })

            random.shuffle(questions)
            return questions[:(num_questions or len(questions))]

        except Exception as e:
            self.logger.warning(f"Could not retrieve curated questions from quiz_bank: {e}")
            return []

    def _get_subject_sources(self, subject=None):
        try:
            if not subject:
                return []
            res = self.retriever.vector_store.collection.get(
                where={"subject": subject},
                include=["metadatas"]
            )
            metas = res.get("metadatas", [])
            seen_files = set()
            sources = []
            for m in metas:
                if isinstance(m, dict) and "file_name" in m:
                    fname = m["file_name"]
                    if fname not in seen_files:
                        seen_files.add(fname)
                        sources.append({
                            "file_name": fname,
                            "page_number": m.get("page_number")
                        })
            return sources[:3]
        except Exception as e:
            self.logger.warning(f"Could not retrieve sources for subject {subject}: {e}")
            return []