import unittest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document
from core.prompt_builder import PromptBuilder
from config.prompts import SYSTEM_PROMPT

class TestPromptBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = PromptBuilder()

    def test_init_success(self):
        self.assertIsNotNone(self.builder.logger)

    def test_build_prompt_success_all_metadata_types(self):
        query = "What are neural networks?"
        docs = [
            Document(page_content="Content of doc1", metadata={"file_name": "network.pdf", "page": 1}),
            Document(page_content="Content of doc2", metadata={"file_path": "folder\\structure\\neurons.pptx"}),
            Document(page_content="Content of doc3", metadata={"source": "http://api/synapses.docx", "page": 10}),
            Document(page_content="Content of doc4", metadata={}),
        ]

        prompt = self.builder.build_prompt(query, docs)

        # Verify format of SYSTEM_PROMPT matches
        # Verify document metadata mapping
        self.assertIn("Document 1\nSource : network.pdf\nPage   : 1", prompt)
        self.assertIn("Content of doc1", prompt)

        self.assertIn("Document 2\nSource : neurons.pptx", prompt)
        self.assertNotIn("Document 2\nSource : neurons.pptx\nPage", prompt)
        self.assertIn("Content of doc2", prompt)

        self.assertIn("Document 3\nSource : synapses.docx\nPage   : 10", prompt)
        self.assertIn("Content of doc3", prompt)

        self.assertIn("Document 4\nSource : Unknown", prompt)
        self.assertIn("Content of doc4", prompt)
        
        # Verify query and context placeholders replaced correctly
        self.assertIn(query, prompt)

    def test_build_prompt_empty_documents(self):
        query = "How to define an array?"
        prompt = self.builder.build_prompt(query, [])

        # Check format is filled with empty context
        expected_prompt = SYSTEM_PROMPT.format(context="", question=query)
        self.assertEqual(prompt, expected_prompt)

    def test_build_prompt_none_page_content(self):
        query = "None page content check"
        mock_doc = MagicMock(spec=Document)
        mock_doc.page_content = None
        mock_doc.metadata = {"file_name": "empty.pdf"}

        prompt = self.builder.build_prompt(query, [mock_doc])

        self.assertIn("Document 1\nSource : empty.pdf", prompt)
        self.assertIn("Content :", prompt)
        # Verify it doesn't crash and replaces None with empty string
        self.assertIn("Content :\n\n------------------------------------------------------------", prompt)

    def test_build_prompt_invalid_documents_type_raises(self):
        with self.assertRaises(TypeError):
            self.builder.build_prompt("query", "not a list")
        with self.assertRaises(TypeError):
            self.builder.build_prompt("query", None)

    def test_build_prompt_non_document_in_list_raises(self):
        docs = [Document(page_content="test"), "not a Document object"]
        with self.assertRaises(TypeError) as context:
            self.builder.build_prompt("query", docs)
        self.assertIn("is not a LangChain Document", str(context.exception))

    @patch("core.prompt_builder.SYSTEM_PROMPT")
    def test_build_prompt_formatting_exception_propagates(self, mock_system_prompt):
        # Trigger formatting exception, e.g., KeyError or ValueError
        mock_system_prompt.format.side_effect = ValueError("Formatting failed")
        
        docs = [Document(page_content="test")]
        with self.assertRaises(ValueError):
            self.builder.build_prompt("query", docs)

if __name__ == "__main__":
    unittest.main()
