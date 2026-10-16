import unittest
from langchain_core.documents import Document
from core.context_builder import ContextBuilder


class TestContextBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = ContextBuilder()

    def test_build_context_empty_list(self):
        self.assertEqual(self.builder.build_context([]), "")

    def test_build_context_invalid_input_type(self):
        with self.assertRaises(TypeError):
            self.builder.build_context("not a list")

    def test_build_context_invalid_document_type(self):
        with self.assertRaises(TypeError):
            self.builder.build_context(["not a Document"])

    def test_build_context_success_formatting(self):
        docs = [
            Document(page_content="Content 1", metadata={"file_name": "dbms.pdf", "page": 12}),
            Document(page_content="Content 2", metadata={"file_path": "path\\to\\os.pptx", "slide": "3-5"}),
        ]

        context = self.builder.build_context(docs)

        self.assertIn("Document 1", context)
        self.assertIn("Source : dbms.pdf", context)
        self.assertIn("Page   : 12", context)
        self.assertIn("Content 1", context)

        self.assertIn("Document 2", context)
        self.assertIn("Source : os.pptx", context)
        self.assertIn("Slide  : 3-5", context)
        self.assertIn("Content 2", context)

    def test_build_context_deduplicates_identical_chunks(self):
        docs = [
            Document(page_content="Identical chunk text", metadata={"file_name": "doc1.pdf"}),
            Document(page_content="Identical chunk text", metadata={"file_name": "doc2.pdf"}),
        ]

        context = self.builder.build_context(docs)
        self.assertIn("Document 1", context)
        self.assertNotIn("Document 2", context)


if __name__ == "__main__":
    unittest.main()
