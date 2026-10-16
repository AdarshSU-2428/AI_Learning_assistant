import unittest
from unittest.mock import MagicMock, patch
from langchain_core.documents import Document

from services.quiz_service import QuizService


class TestQuizService(unittest.TestCase):
    @patch("services.quiz_service.Retriever")
    @patch("services.quiz_service.Reranker")
    @patch("services.quiz_service.RelevanceGate")
    @patch("services.quiz_service.PromptBuilder")
    @patch("services.quiz_service.LLMClient")
    @patch("services.quiz_service.SafetyManager")
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

        # Default passthrough behavior for safety manager
        self.mock_safety.sanitize_input.side_effect = lambda x: x.strip()
        self.mock_safety.sanitize_output.side_effect = lambda x: x

        # Default context builder mock
        self.mock_context_builder = MagicMock()
        self.mock_context_builder.build_context.return_value = "Binary Search Context"
        self.mock_prompt.context_builder = self.mock_context_builder

        self.service = QuizService()

    def test_generate_quiz_empty_topic_raises_error(self):
        with self.assertRaises(ValueError):
            self.service.generate_quiz("")

        with self.assertRaises(ValueError):
            self.service.generate_quiz("   ")

    def test_generate_quiz_empty_after_sanitization(self):
        self.mock_safety.sanitize_input.side_effect = None
        self.mock_safety.sanitize_input.return_value = ""
        with self.assertRaises(ValueError):
            self.service.generate_quiz("some input")

    def test_generate_quiz_no_documents_retrieved(self):
        self.mock_retriever.retrieve.return_value = []
        res = self.service.generate_quiz("Nonexistent Topic")
        self.assertFalse(res["is_relevant"])
        self.assertEqual(res["questions"], [])
        self.assertIn("No relevant course materials found", res["message"])

    def test_generate_quiz_out_of_syllabus_rejected(self):
        doc1 = Document(page_content="irrelevant content", metadata={"file_name": "doc.pdf"})
        self.mock_retriever.retrieve.return_value = [doc1]
        self.mock_reranker.score_documents.return_value = [(doc1, 0.00001)]
        self.mock_gate.evaluate_relevance.return_value = ([], False)

        res = self.service.generate_quiz("Cooking Recipes", subject="OS")
        self.assertFalse(res["is_relevant"])
        self.assertEqual(res["questions"], [])
        self.assertIn("not covered in your uploaded course materials", res["message"])

    def test_generate_quiz_success(self):
        doc1 = Document(page_content="Binary Search is divide and conquer.", metadata={"file_name": "DAA.pdf", "page_number": 5})
        self.mock_retriever.retrieve.return_value = [doc1]
        self.mock_reranker.score_documents.return_value = [(doc1, 0.85)]
        self.mock_gate.evaluate_relevance.return_value = ([doc1], True)

        mock_llm_json = """
        [
            {
                "id": 1,
                "question": "What is the time complexity of Binary Search?",
                "options": ["A) O(1)", "B) O(log n)", "C) O(n)", "D) O(n^2)"],
                "correct_answer": "B",
                "explanation": "Binary search divides the search space in half.",
                "hint": "Divide and conquer."
            }
        ]
        """
        self.mock_llm.generate_response.return_value = mock_llm_json

        res = self.service.generate_quiz("Binary Search", subject="DAA", num_questions=1, difficulty="Medium")
        self.assertTrue(res["is_relevant"])
        self.assertEqual(len(res["questions"]), 1)
        self.assertEqual(res["questions"][0]["correct_answer"], "B")
        self.assertEqual(res["sources"][0]["file_name"], "DAA.pdf")
        self.assertEqual(res["sources"][0]["page_number"], 5)

    def test_parse_quiz_json_with_code_fences(self):
        fenced_json = """```json
        [
            {
                "id": 1,
                "question": "Sample?",
                "options": ["A) 1", "B) 2"],
                "correct_answer": "A",
                "explanation": "Exp",
                "hint": "H"
            }
        ]
        ```"""
        parsed = self.service._parse_quiz_json(fenced_json)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["id"], 1)

    def test_parse_quiz_json_fallback_regex(self):
        chatty_response = """Here is your quiz:
        [
            {
                "id": 1,
                "question": "Sample?",
                "options": ["A) 1", "B) 2"],
                "correct_answer": "A",
                "explanation": "Exp",
                "hint": "H"
            }
        ]
        Hope you liked it!"""
        parsed = self.service._parse_quiz_json(chatty_response)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["id"], 1)

    def test_evaluate_submission_perfect_score(self):
        quiz_questions = [
            {"id": 1, "question": "Q1", "correct_answer": "A", "explanation": "E1", "hint": "H1"},
            {"id": 2, "question": "Q2", "correct_answer": "C", "explanation": "E2", "hint": "H2"},
        ]
        user_answers = {1: "A", 2: "C"}

        evaluation = self.service.evaluate_submission(quiz_questions, user_answers)
        self.assertEqual(evaluation["score"], 2)
        self.assertEqual(evaluation["total"], 2)
        self.assertEqual(evaluation["percentage"], 100.0)
        self.assertTrue(evaluation["details"][0]["is_correct"])
        self.assertTrue(evaluation["details"][1]["is_correct"])

    def test_evaluate_submission_partial_score(self):
        quiz_questions = [
            {"id": 1, "question": "Q1", "correct_answer": "A", "explanation": "E1", "hint": "H1"},
            {"id": 2, "question": "Q2", "correct_answer": "C", "explanation": "E2", "hint": "H2"},
            {"id": 3, "question": "Q3", "correct_answer": "D", "explanation": "E3", "hint": "H3"},
            {"id": 4, "question": "Q4", "correct_answer": "B", "explanation": "E4", "hint": "H4"},
        ]
        user_answers = {1: "A", 2: "B", 3: "D", 4: "A"}  # Q1 and Q3 are correct

        evaluation = self.service.evaluate_submission(quiz_questions, user_answers)
        self.assertEqual(evaluation["score"], 2)
        self.assertEqual(evaluation["total"], 4)
        self.assertEqual(evaluation["percentage"], 50.0)
        self.assertTrue(evaluation["details"][0]["is_correct"])
        self.assertFalse(evaluation["details"][1]["is_correct"])
        self.assertTrue(evaluation["details"][2]["is_correct"])
        self.assertFalse(evaluation["details"][3]["is_correct"])

    def test_evaluate_submission_empty_quiz(self):
        evaluation = self.service.evaluate_submission([], {})
        self.assertEqual(evaluation["score"], 0)
        self.assertEqual(evaluation["total"], 0)
        self.assertEqual(evaluation["percentage"], 0.0)
        self.assertEqual(evaluation["details"], [])


if __name__ == "__main__":
    unittest.main()
