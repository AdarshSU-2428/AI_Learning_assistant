import unittest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document
from core.vector_store import VectorStore

class TestVectorStore(unittest.TestCase):
    @patch("core.vector_store.chromadb.PersistentClient")
    def setUp(self, mock_client_cls):
        self.mock_client = MagicMock()
        self.mock_collection = MagicMock()
        
        mock_client_cls.return_value = self.mock_client
        self.mock_client.get_or_create_collection.return_value = self.mock_collection
        
        self.vector_store = VectorStore(persist_directory="dummy_dir", collection_name="dummy_col")

    def test_init_success(self):
        self.mock_client.get_or_create_collection.assert_called_once_with(name="dummy_col")

    def test_store_success(self):
        documents = [
            Document(page_content="Text 1", metadata={"source": "doc1"}),
            Document(page_content="Text 2", metadata={"source": "doc2"}),
        ]
        import numpy as np
        embeddings = np.array([[0.1, 0.2], [0.3, 0.4]])

        stored_count = self.vector_store.store(documents, embeddings)

        # Assert correct count returned
        self.assertEqual(stored_count, 2)
        
        # Verify collection.add was called correctly
        self.mock_collection.add.assert_called_once()
        _, kwargs = self.mock_collection.add.call_args
        
        self.assertEqual(len(kwargs["ids"]), 2)
        self.assertEqual(kwargs["documents"], ["Text 1", "Text 2"])
        self.assertEqual(kwargs["embeddings"], [[0.1, 0.2], [0.3, 0.4]])
        self.assertEqual(kwargs["metadatas"], [{"source": "doc1"}, {"source": "doc2"}])

    def test_store_empty_documents(self):
        stored_count = self.vector_store.store([], [])
        self.assertEqual(stored_count, 0)
        self.mock_collection.add.assert_not_called()

    def test_store_mismatch_length_raises(self):
        documents = [Document(page_content="Text 1")]
        embeddings = [[0.1, 0.2], [0.3, 0.4]] # length 2
        
        with self.assertRaises(ValueError):
            self.vector_store.store(documents, embeddings)

if __name__ == "__main__":
    unittest.main()
