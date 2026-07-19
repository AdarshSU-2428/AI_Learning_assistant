import unittest
from unittest.mock import patch, MagicMock
from core.llm_client import LLMClient

class TestLLMClient(unittest.TestCase):
    @patch("core.llm_client.Groq")
    def setUp(self, mock_groq_cls):
        self.mock_groq_instance = MagicMock()
        mock_groq_cls.return_value = self.mock_groq_instance
        
        # Instantiate LLMClient
        self.llm_client = LLMClient()

    def test_init_success(self):
        self.assertIsNotNone(self.llm_client.client)
        self.assertEqual(self.llm_client.model, "qwen/qwen3.6-27b")

    def test_generate_response_success(self):
        prompt = "Hello AI!"
        expected_response = "Hello human!"
        
        # Mock Completion response structure: response.choices[0].message.content
        mock_choice = MagicMock()
        mock_choice.message.content = expected_response
        
        mock_completions = MagicMock()
        mock_completions.choices = [mock_choice]
        
        self.mock_groq_instance.chat.completions.create.return_value = mock_completions

        response = self.llm_client.generate_response(prompt)

        self.assertEqual(response, expected_response)
        self.mock_groq_instance.chat.completions.create.assert_called_once_with(
            model="qwen/qwen3.6-27b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_completion_tokens=1024
        )

    def test_generate_response_invalid_prompt_type_raises(self):
        with self.assertRaises(TypeError):
            self.llm_client.generate_response(123)
        with self.assertRaises(TypeError):
            self.llm_client.generate_response(None)
        self.mock_groq_instance.chat.completions.create.assert_not_called()

    def test_generate_response_empty_prompt_raises(self):
        with self.assertRaises(ValueError):
            self.llm_client.generate_response("")
        with self.assertRaises(ValueError):
            self.llm_client.generate_response("   ")
        self.mock_groq_instance.chat.completions.create.assert_not_called()

    def test_generate_response_exception_propagates(self):
        prompt = "Will fail"
        self.mock_groq_instance.chat.completions.create.side_effect = Exception("API error")
        
        # Directly mock the logger on the instance
        self.llm_client.logger = MagicMock()
        
        with self.assertRaises(Exception):
            self.llm_client.generate_response(prompt)

        self.llm_client.logger.exception.assert_called_once_with("Failed to generate response from LLM.")

if __name__ == "__main__":
    unittest.main()
