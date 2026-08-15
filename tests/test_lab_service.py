import unittest
from unittest.mock import MagicMock, patch
from langchain_core.documents import Document
from services.lab_service import LabService


class TestLabService(unittest.TestCase):
    @patch("services.lab_service.Retriever")
    @patch("services.lab_service.Reranker")
    @patch("services.lab_service.RelevanceGate")
    @patch("services.lab_service.PromptBuilder")
    @patch("services.lab_service.LLMClient")
    @patch("services.lab_service.SafetyManager")
    def setUp(
        self,
        mock_safety_cls,
        mock_llm_cls,
        mock_prompt_cls,
        mock_gate_cls,
        mock_reranker_cls,
        mock_retriever_cls,
    ):
        self.mock_lab_retriever = MagicMock()
        self.mock_notes_retriever = MagicMock()
        self.mock_reranker = MagicMock()
        self.mock_gate = MagicMock()
        self.mock_prompt = MagicMock()
        self.mock_llm = MagicMock()
        self.mock_safety = MagicMock()

        mock_retriever_cls.side_effect = [self.mock_lab_retriever, self.mock_notes_retriever]
        mock_reranker_cls.return_value = self.mock_reranker
        mock_gate_cls.return_value = self.mock_gate
        mock_prompt_cls.return_value = self.mock_prompt
        mock_llm_cls.return_value = self.mock_llm
        mock_safety_cls.return_value = self.mock_safety

        self.service = LabService()

    def test_chat_empty_question_raises(self):
        with self.assertRaises(ValueError):
            self.service.chat("")

        with self.assertRaises(ValueError):
            self.service.chat("   ")

    def test_chat_no_documents_retrieved(self):
        self.mock_safety.sanitize_input.return_value = "Implement Merge Sort in C"
        self.mock_lab_retriever.retrieve.return_value = []
        self.mock_notes_retriever.retrieve.return_value = []

        result = self.service.chat("Implement Merge Sort in C", subject="DAA")

        self.assertFalse(result["is_relevant"])
        self.assertEqual(result["sources"], [])
        self.mock_lab_retriever.retrieve.assert_called_once()
        self.mock_notes_retriever.retrieve.assert_called_once()

    def test_chat_fallback_to_notes_when_lab_empty(self):
        mock_doc = Document(page_content="Merge sort divides the array into halves.", metadata={"file_name": "DAA_Notes.pdf"})
        self.mock_safety.sanitize_input.return_value = "Implement Merge Sort"
        self.mock_lab_retriever.retrieve.return_value = []
        self.mock_notes_retriever.retrieve.return_value = [mock_doc]
        self.mock_reranker.score_documents.return_value = [(mock_doc, 0.45)]
        self.mock_gate.evaluate_relevance.return_value = ([mock_doc], True)
        self.mock_prompt.build_messages.return_value = [{"role": "user", "content": "prompt"}]
        self.mock_llm.generate_response.return_value = "```c\nvoid mergeSort() {}\n```"
        self.mock_safety.sanitize_output.return_value = "```c\nvoid mergeSort() {}\n```"

        result = self.service.chat("Implement Merge Sort", subject="DAA")

        self.assertTrue(result["is_relevant"])
        self.assertIn("void mergeSort", result["answer"])
        self.assertEqual(len(result["sources"]), 1)
        self.mock_lab_retriever.retrieve.assert_called_once()
        self.mock_notes_retriever.retrieve.assert_called_once()

    def test_chat_rejected_by_relevance_gate(self):
        mock_doc = Document(page_content="Unrelated text", metadata={"file_name": "manual.pdf"})
        self.mock_safety.sanitize_input.return_value = "How to bake a cake"
        self.mock_lab_retriever.retrieve.return_value = [mock_doc]
        self.mock_reranker.score_documents.return_value = [(mock_doc, 0.00001)]
        self.mock_gate.evaluate_relevance.return_value = ([], False)

        result = self.service.chat("How to bake a cake", subject="DAA")

        self.assertFalse(result["is_relevant"])
        self.assertEqual(result["sources"], [])
        self.assertIn("syllabus", result["answer"].lower())

    def test_chat_success_returns_structured_answer(self):
        mock_doc = Document(page_content="Full Adder Truth Table", metadata={"file_name": "DEC_Lab_Manual.pdf"})
        self.mock_safety.sanitize_input.return_value = "Design Full Adder"
        self.mock_lab_retriever.retrieve.return_value = [mock_doc]
        self.mock_reranker.score_documents.return_value = [(mock_doc, 0.85)]
        self.mock_gate.evaluate_relevance.return_value = ([mock_doc], True)
        self.mock_prompt.build_messages.return_value = [{"role": "user", "content": "prompt"}]
        self.mock_llm.generate_response.return_value = "### Full Adder\nSum = A XOR B XOR Cin"
        self.mock_safety.sanitize_output.return_value = "### Full Adder\nSum = A XOR B XOR Cin"

        result = self.service.chat("Design Full Adder", subject="DEC")

        self.assertTrue(result["is_relevant"])
        self.assertEqual(result["answer"], "### Full Adder\nSum = A XOR B XOR Cin")
        self.assertEqual(len(result["sources"]), 1)

    def test_process_query_alias(self):
        with patch.object(self.service, "chat", return_value={"answer": "ok"}) as mock_chat:
            res = self.service.process_query("test", subject="OS")
            self.assertEqual(res, {"answer": "ok"})
            mock_chat.assert_called_once_with("test", subject="OS")


if __name__ == "__main__":
    unittest.main()
