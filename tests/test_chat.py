import unittest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document
from services.chat_service import ChatService

class TestChatService(unittest.TestCase):
    @patch("services.chat_service.Retriever")
    @patch("services.chat_service.Reranker")
    @patch("services.chat_service.PromptBuilder")
    @patch("services.chat_service.LLMClient")
    def setUp(self, mock_llm_cls, mock_pb_cls, mock_reranker_cls, mock_retriever_cls):
        self.mock_retriever = MagicMock()
        self.mock_reranker = MagicMock()
        self.mock_pb = MagicMock()
        self.mock_llm = MagicMock()

        mock_retriever_cls.return_value = self.mock_retriever
        mock_reranker_cls.return_value = self.mock_reranker
        mock_pb_cls.return_value = self.mock_pb
        mock_llm_cls.return_value = self.mock_llm

        self.chat_service = ChatService()

    def test_ask_empty_question_raises(self):
        with self.assertRaises(ValueError):
            self.chat_service.ask("")
        with self.assertRaises(ValueError):
            self.chat_service.ask("   ")

    def test_ask_no_documents_retrieved(self):
        self.mock_retriever.retrieve.return_value = []
        
        result = self.chat_service.ask("Test question")
        
        self.assertEqual(result["query"], "Test question")
        self.assertEqual(result["answer"], "I couldn't find any relevant information in the indexed documents.")
        self.assertEqual(result["documents"], [])
        
        self.mock_retriever.retrieve.assert_called_once_with("Test question")
        self.mock_reranker.rerank.assert_not_called()
        self.mock_pb.build_prompt.assert_not_called()
        self.mock_llm.generate_response.assert_not_called()

    def test_ask_success(self):
        question = "What is machine learning?"
        mock_docs = [Document(page_content="ML is...")]
        mock_reranked = [Document(page_content="ML is...")]
        mock_prompt = "Formatted System Prompt and Question"
        mock_answer = "Machine learning is a field of AI."

        self.mock_retriever.retrieve.return_value = mock_docs
        self.mock_reranker.rerank.return_value = mock_reranked
        self.mock_pb.build_prompt.return_value = mock_prompt
        self.mock_llm.generate_response.return_value = mock_answer

        result = self.chat_service.ask(question)

        self.assertEqual(result["query"], question)
        self.assertEqual(result["answer"], mock_answer)
        self.assertEqual(result["documents"], mock_reranked)

        self.mock_retriever.retrieve.assert_called_once_with(question)
        self.mock_reranker.rerank.assert_called_once_with(question, mock_docs)
        self.mock_pb.build_prompt.assert_called_once_with(question, mock_reranked)
        self.mock_llm.generate_response.assert_called_once_with(mock_prompt)

    def test_ask_llm_failure_returns_unexpected_error(self):
        question = "Test"
        mock_docs = [Document(page_content="doc")]
        mock_reranked = [Document(page_content="doc")]
        mock_prompt = "prompt"

        self.mock_retriever.retrieve.return_value = mock_docs
        self.mock_reranker.rerank.return_value = mock_reranked
        self.mock_pb.build_prompt.return_value = mock_prompt
        self.mock_llm.generate_response.return_value = None  # Simulates API error returning None

        result = self.chat_service.ask(question)

        self.assertEqual(result["query"], question)
        self.assertIn("An unexpected error occurred", result["answer"])
        self.assertEqual(result["documents"], [])

    def test_ask_retriever_failure_returns_unexpected_error(self):
        question = "Test"
        self.mock_retriever.retrieve.side_effect = RuntimeError("DB down")

        result = self.chat_service.ask(question)

        self.assertEqual(result["query"], question)
        self.assertIn("An unexpected error occurred", result["answer"])
        self.assertEqual(result["documents"], [])

    def test_ask_value_error_caught_and_returned(self):
        question = "Test"
        self.mock_retriever.retrieve.side_effect = ValueError("Some validation error message")

        result = self.chat_service.ask(question)

        self.assertEqual(result["query"], question)
        self.assertEqual(result["answer"], "Some validation error message")
        self.assertEqual(result["documents"], [])

if __name__ == "__main__":
    unittest.main()
