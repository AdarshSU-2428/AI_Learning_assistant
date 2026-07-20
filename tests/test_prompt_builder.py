import unittest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document
from core.prompt_builder import PromptBuilder
from config.prompts import SYSTEM_PROMPT, USER_PROMPT

class TestPromptBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = PromptBuilder()

    def test_init_success(self):
        self.assertIsNotNone(self.builder.logger)

    def test_build_messages_success_all_metadata_types(self):
        query = "What are neural networks?"
        docs = [
            Document(page_content="Content of doc1", metadata={"file_name": "network.pdf", "page": 1}),
            Document(page_content="Content of doc2", metadata={"file_path": "folder\\structure\\neurons.pptx"}),
            Document(page_content="Content of doc3", metadata={"source": "http://api/synapses.docx", "page": 10}),
            Document(page_content="Content of doc4", metadata={}),
        ]

        messages = self.builder.build_messages(SYSTEM_PROMPT, USER_PROMPT, query, docs)

        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[0]["content"], SYSTEM_PROMPT)

        self.assertEqual(messages[1]["role"], "user")
        user_content = messages[1]["content"]

        # Verify document metadata mapping
        self.assertIn("Document 1\nSource : network.pdf\nPage   : 1", user_content)
        self.assertIn("Content of doc1", user_content)

        self.assertIn("Document 2\nSource : neurons.pptx", user_content)
        self.assertNotIn("Document 2\nSource : neurons.pptx\nPage", user_content)
        self.assertIn("Content of doc2", user_content)

        self.assertIn("Document 3\nSource : synapses.docx\nPage   : 10", user_content)
        self.assertIn("Content of doc3", user_content)

        self.assertIn("Document 4\nSource : Unknown", user_content)
        self.assertIn("Content of doc4", user_content)
        
        # Verify query and context placeholders replaced correctly
        self.assertIn(query, user_content)

    def test_build_messages_empty_documents(self):
        query = "How to define an array?"
        messages = self.builder.build_messages(SYSTEM_PROMPT, USER_PROMPT, query, [])

        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[0]["content"], SYSTEM_PROMPT)

        self.assertEqual(messages[1]["role"], "user")
        expected_user_content = USER_PROMPT.format(context="", question=query)
        self.assertEqual(messages[1]["content"], expected_user_content)

    def test_build_messages_none_page_content(self):
        query = "None page content check"
        mock_doc = MagicMock(spec=Document)
        mock_doc.page_content = None
        mock_doc.metadata = {"file_name": "empty.pdf"}

        messages = self.builder.build_messages(SYSTEM_PROMPT, USER_PROMPT, query, [mock_doc])
        user_content = messages[1]["content"]

        self.assertIn("Document 1\nSource : empty.pdf", user_content)
        self.assertIn("Content :", user_content)
        # Verify it doesn't crash and replaces None with empty string
        self.assertIn("Content :\n\n------------------------------------------------------------", user_content)

    def test_build_messages_invalid_template_type_raises(self):
        with self.assertRaises(TypeError):
            self.builder.build_messages(123, USER_PROMPT, "query", [])
        with self.assertRaises(TypeError):
            self.builder.build_messages(SYSTEM_PROMPT, 123, "query", [])
        with self.assertRaises(TypeError):
            self.builder.build_messages(None, USER_PROMPT, "query", [])

    def test_build_messages_invalid_documents_type_raises(self):
        with self.assertRaises(TypeError):
            self.builder.build_messages(SYSTEM_PROMPT, USER_PROMPT, "query", "not a list")
        with self.assertRaises(TypeError):
            self.builder.build_messages(SYSTEM_PROMPT, USER_PROMPT, "query", None)

    def test_build_messages_non_document_in_list_raises(self):
        docs = [Document(page_content="test"), "not a Document object"]
        with self.assertRaises(TypeError) as context:
            self.builder.build_messages(SYSTEM_PROMPT, USER_PROMPT, "query", docs)
        self.assertIn("is not a LangChain Document", str(context.exception))

    def test_build_messages_formatting_exception_propagates(self):
        mock_template = MagicMock(spec=str)
        mock_template.format.side_effect = ValueError("Formatting failed")
        
        docs = [Document(page_content="test")]
        with self.assertRaises(ValueError):
            self.builder.build_messages(SYSTEM_PROMPT, mock_template, "query", docs)

if __name__ == "__main__":
    unittest.main()
