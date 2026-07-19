import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Import the FastAPI app instance from backend.app
from backend.app import app

class TestBackendAPI(unittest.TestCase):
    @patch("backend.app.app_service")
    def setUp(self, mock_app_service):
        self.mock_app_service = mock_app_service
        self.client = TestClient(app)

    @patch("backend.routes.app_service")
    def test_chat_success(self, mock_route_service):
        # Precondition
        mock_response = {
            "query": "What is Transformer?",
            "answer": "A Transformer is a deep learning model.",
            "sources": []
        }
        mock_route_service.chat.return_value = mock_response

        # Action
        response = self.client.post("/chat", json={"query": "What is Transformer?"})

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), mock_response)
        mock_route_service.chat.assert_called_once_with("What is Transformer?")

    @patch("backend.routes.app_service")
    def test_chat_validation_error_propagates(self, mock_route_service):
        # Precondition (ValueError raised by service)
        mock_route_service.chat.side_effect = ValueError("Question cannot be empty.")

        # Action
        response = self.client.post("/chat", json={"query": ""})

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Question cannot be empty.")
        mock_route_service.chat.assert_called_once_with("")

if __name__ == "__main__":
    unittest.main()
