import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from backend.backend_app import app


class TestBackendAPI(unittest.TestCase):
    @patch("backend.backend_app.app_service")
    def setUp(self, mock_app_service):
        self.mock_app_service = mock_app_service
        self.client = TestClient(app)

    @patch("backend.routes.app_service")
    def test_chat_success(self, mock_route_service):
        mock_response = {
            "query": "What is Transformer?",
            "answer": "A Transformer is a deep learning model.",
            "sources": [],
        }
        mock_route_service.chat.return_value = mock_response

        response = self.client.post("/chat", json={"query": "What is Transformer?"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), mock_response)
        mock_route_service.chat.assert_called_once_with("What is Transformer?", subject=None)

    @patch("backend.routes.app_service")
    def test_chat_validation_error_propagates(self, mock_route_service):
        mock_route_service.chat.side_effect = ValueError("Question cannot be empty.")

        response = self.client.post("/chat", json={"query": ""})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Question cannot be empty.")
        mock_route_service.chat.assert_called_once_with("", subject=None)

    @patch("backend.routes.app_service")
    def test_generate_quiz_success(self, mock_route_service):
        mock_response = {
            "topic": "Binary Search",
            "difficulty": "Medium",
            "questions": [{"id": 1, "question": "Q1"}],
            "sources": [{"file_name": "DAA.pdf", "page_number": 5}],
            "is_relevant": True,
            "message": "Quiz generated successfully."
        }
        mock_route_service.generate_quiz.return_value = mock_response

        payload = {
            "topic": "Binary Search",
            "subject": "DAA",
            "num_questions": 5,
            "difficulty": "Medium"
        }
        response = self.client.post("/quiz/generate", json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["topic"], "Binary Search")
        mock_route_service.generate_quiz.assert_called_once_with(
            topic="Binary Search",
            subject="DAA",
            num_questions=5,
            difficulty="Medium"
        )

    @patch("backend.routes.app_service")
    def test_evaluate_quiz_success(self, mock_route_service):
        mock_response = {
            "score": 5,
            "total": 5,
            "percentage": 100.0,
            "details": []
        }
        mock_route_service.evaluate_quiz_submission.return_value = mock_response

        payload = {
            "quiz_questions": [{"id": 1}],
            "user_answers": {"1": "A"}
        }
        response = self.client.post("/quiz/evaluate", json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["score"], 5)
        self.assertEqual(response.json()["percentage"], 100.0)


if __name__ == "__main__":
    unittest.main()
