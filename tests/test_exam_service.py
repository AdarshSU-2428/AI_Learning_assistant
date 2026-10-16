import unittest
from unittest.mock import MagicMock, patch
from langchain_core.documents import Document
from services.exam_service import ExamService


class TestExamService(unittest.TestCase):
    @patch("services.exam_service.Retriever")
    @patch("services.exam_service.Reranker")
    @patch("services.exam_service.RelevanceGate")
    @patch("services.exam_service.PromptBuilder")
    @patch("services.exam_service.LLMClient")
    @patch("services.exam_service.SafetyManager")
    def setUp(
        self,
        mock_safety_cls,
        mock_llm_cls,
        mock_prompt_cls,
        mock_gate_cls,
        mock_reranker_cls,
        mock_retriever_cls,
    ):
        self.mock_retriever = MagicMock()
        self.mock_reranker = MagicMock()
        self.mock_gate = MagicMock()
        self.mock_prompt = MagicMock()
        self.mock_llm = MagicMock()
        self.mock_safety = MagicMock()

        mock_retriever_cls.return_value = self.mock_retriever
        mock_reranker_cls.return_value = self.mock_reranker
        mock_gate_cls.return_value = self.mock_gate
        mock_prompt_cls.return_value = self.mock_prompt
        mock_llm_cls.return_value = self.mock_llm
        mock_safety_cls.return_value = self.mock_safety

        self.service = ExamService()

    def test_generate_exam_empty_subject_raises(self):
        with self.assertRaises(ValueError):
            self.service.generate_exam("")

        with self.assertRaises(ValueError):
            self.service.generate_exam("   ")

    def test_generate_exam_no_documents_retrieved(self):
        self.mock_safety.sanitize_input.return_value = "DAA"
        self.mock_retriever.retrieve.return_value = []

        result = self.service.generate_exam("DAA")

        self.assertFalse(result["is_relevant"])
        self.assertEqual(result["questions"], [])
        self.assertIn("don't have enough syllabus course notes", result["message"])

    def test_generate_exam_success(self):
        mock_doc = Document(page_content="Dynamic Programming principles", metadata={"file_name": "DAA_Notes.pdf", "page": 4})
        self.mock_safety.sanitize_input.return_value = "DAA"
        self.mock_retriever.retrieve.return_value = [mock_doc]
        self.mock_reranker.score_documents.return_value = [(mock_doc, 0.85)]
        self.mock_gate.evaluate_relevance.return_value = ([mock_doc], True)

        mock_json_response = """{
            "exam_title": "DAA Exam Paper",
            "subject": "DAA",
            "total_marks": 9,
            "questions": [
                {
                    "id": 1,
                    "section": "Section A (1 Mark)",
                    "marks": 1,
                    "question_title": "DP Definition",
                    "question_text": "Define Dynamic Programming.",
                    "model_answer": "DP is an optimization technique...",
                    "rubric_checklist": ["Correct definition (1 Mark)"]
                },
                {
                    "id": 2,
                    "section": "Section B (3 Marks)",
                    "marks": 3,
                    "question_title": "Principle of Optimality",
                    "question_text": "Explain principle of optimality.",
                    "model_answer": "Principle of optimality states...",
                    "rubric_checklist": ["Definition (1 Mark)", "Proof sketch (2 Marks)"]
                },
                {
                    "id": 3,
                    "section": "Section C (5 Marks)",
                    "marks": 5,
                    "question_title": "0/1 Knapsack",
                    "question_text": "Derive 0/1 Knapsack recurrence.",
                    "model_answer": "Recurrence is V[i,w] = ...",
                    "rubric_checklist": ["Setup (2 Marks)", "Recurrence equation (3 Marks)"]
                }
            ]
        }"""
        self.mock_llm.generate_response.return_value = mock_json_response

        result = self.service.generate_exam("DAA", num_questions=3)

        self.assertTrue(result["is_relevant"])
        self.assertEqual(len(result["questions"]), 3)
        self.assertEqual(result["total_marks"], 9)
        self.assertEqual(result["questions"][0]["marks"], 1)
        self.assertEqual(result["questions"][1]["marks"], 3)
        self.assertEqual(result["questions"][2]["marks"], 5)


if __name__ == "__main__":
    unittest.main()
