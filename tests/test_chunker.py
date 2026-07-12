import unittest
from core.chunker import Chunker

class TestChunker(unittest.TestCase):
    def setUp(self):
        # Set up a chunker with small size for easier testing
        self.chunker = Chunker(chunk_size=100, chunk_overlap=10)

    def test_init_defaults(self):
        default_chunker = Chunker()
        self.assertEqual(default_chunker.chunk_size, 1000)
        self.assertEqual(default_chunker.chunk_overlap, 200)

    def test_chunk_text_success(self):
        # Text long enough to be split into multiple chunks (since chunk_size=100)
        text = "This is a short paragraph. This is another sentence that will make the text longer so it splits. " * 3
        metadata = {"doc_id": "doc_123"}
        
        chunks = self.chunker.chunk_text(text, metadata)
        
        # Verify chunks list is returned and has multiple items
        self.assertTrue(len(chunks) > 1)
        
        # Verify metadata and chunk numbering
        for index, chunk in enumerate(chunks):
            self.assertEqual(chunk.metadata["doc_id"], "doc_123")
            self.assertEqual(chunk.metadata["chunk_id"], index)
            self.assertTrue(len(chunk.page_content) <= 100)

    def test_chunk_text_invalid_type(self):
        with self.assertRaises(TypeError):
            self.chunker.chunk_text(12345, {})

    def test_chunk_text_with_none_metadata(self):
        text = "This is a test sentence to check if chunking works properly."
        chunks = self.chunker.chunk_text(text, None)
        self.assertEqual(len(chunks), 1)
        self.assertIn("chunk_id", chunks[0].metadata)
        self.assertEqual(list(chunks[0].metadata.keys()), ["chunk_id"])

if __name__ == "__main__":
    unittest.main()
    