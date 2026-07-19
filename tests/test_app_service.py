import unittest
from unittest.mock import patch, MagicMock
from services.app_service import ApplicationService

class TestApplicationService(unittest.TestCase):
    @patch("services.app_service.ChatService")
    @patch("services.app_service.IndexingService")
    def setUp(self, mock_indexing_cls, mock_chat_cls):
        self.mock_chat = MagicMock()
        self.mock_indexing = MagicMock()
        
        mock_chat_cls.return_value = self.mock_chat
        mock_indexing_cls.return_value = self.mock_indexing
        
        self.service = ApplicationService()

    def test_init(self):
        self.assertEqual(self.service.chat_service, self.mock_chat)
        self.assertEqual(self.service.indexing_service, self.mock_indexing)

    def test_index_documents(self):
        self.mock_indexing.index_directory.return_value = {"status": "success"}
        
        result = self.service.index_documents("dummy/path")
        
        self.assertEqual(result, {"status": "success"})
        self.mock_indexing.index_directory.assert_called_once_with("dummy/path")

    def test_chat(self):
        self.mock_chat.chat.return_value = {"answer": "result"}
        
        result = self.service.chat("hello")
        
        self.assertEqual(result, {"answer": "result"})
        self.mock_chat.chat.assert_called_once_with("hello")

if __name__ == "__main__":
    unittest.main()
