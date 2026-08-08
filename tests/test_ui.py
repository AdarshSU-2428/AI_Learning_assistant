import unittest
import sys

from frontend.ui.components import parse_source_info, get_user_friendly_error_message
from frontend.ui.api_client import (
    BackendConnectionError,
    BackendTimeoutError,
    BackendResponseError,
    InvalidBackendResponseError,
    APIClientError,
)


class TestUIComponents(unittest.TestCase):
    def test_parse_source_info_dict_with_metadata(self):
        item = {
            "metadata": {
                "source": "C:\\Users\\Student\\Documents\\Physics_Ch1.pdf",
                "page": 3,
            }
        }
        filename, unit_info = parse_source_info(item)
        self.assertEqual(filename, "Physics_Ch1.pdf")
        self.assertEqual(unit_info, ("Page", 3))

    def test_parse_source_info_flat_dict(self):
        item = {
            "source": "/var/data/docs/Chemistry_Lab.pptx",
            "slide": 5,
        }
        filename, unit_info = parse_source_info(item)
        self.assertEqual(filename, "Chemistry_Lab.pptx")
        self.assertEqual(unit_info, ("Slide", 5))

    def test_parse_source_info_string(self):
        item = "D:\\Study_Notes\\Biology_Summary.pdf"
        filename, unit_info = parse_source_info(item)
        self.assertEqual(filename, "Biology_Summary.pdf")
        self.assertIsNone(unit_info)

    def test_parse_source_info_invalid(self):
        self.assertIsNone(parse_source_info(None))
        self.assertIsNone(parse_source_info({}))
        self.assertIsNone(parse_source_info(123))

    def test_error_message_connection_error(self):
        exc = BackendConnectionError("Unable to connect")
        msg = get_user_friendly_error_message(exc)
        self.assertEqual(
            msg,
            "AI Learning Assistant is temporarily unavailable. Please try again shortly.",
        )

    def test_error_message_timeout_error(self):
        exc = BackendTimeoutError("Timeout occurred")
        msg = get_user_friendly_error_message(exc)
        self.assertEqual(
            msg, "The response is taking longer than expected. Please try again."
        )

    def test_error_message_invalid_response_error(self):
        exc = InvalidBackendResponseError("JSON decode error")
        msg = get_user_friendly_error_message(exc)
        self.assertEqual(
            msg, "Something went wrong while preparing the response. Please try again."
        )

    def test_error_message_invalid_question_error(self):
        exc = BackendResponseError("Question cannot be empty.")
        msg = get_user_friendly_error_message(exc)
        self.assertEqual(msg, "Please enter a valid question.")

    def test_error_message_generic_backend_error(self):
        exc = BackendResponseError("Backend returned HTTP 500.")
        msg = get_user_friendly_error_message(exc)
        self.assertEqual(
            msg, "Something went wrong while preparing the response. Please try again."
        )

    def test_error_message_unexpected_error(self):
        exc = Exception("Random crash")
        msg = get_user_friendly_error_message(exc)
        self.assertEqual(msg, "Something went wrong. Please try again.")

    def test_no_backend_imports_in_frontend(self):
        """Verify that UI modules do not import backend or core components."""
        ui_modules = [
            "frontend.ui.components",
            "frontend.ui.sidebar",
            "frontend.ui.learning_interface",
            "frontend.ui.quiz_interface",
            "frontend.frontend_app",
        ]

        for mod_name in ui_modules:
            if mod_name in sys.modules:
                mod = sys.modules[mod_name]
                with open(mod.__file__, "r", encoding="utf-8") as f:
                    content = f.read()

                for line in content.splitlines():
                    if line.strip().startswith(("import ", "from ")):
                        for forbidden in ["backend", "services", "core"]:
                            self.assertNotIn(
                                f"import {forbidden}",
                                line,
                                f"Forbidden import found in {mod_name}: {line}",
                            )
                            self.assertNotIn(
                                f"from {forbidden}",
                                line,
                                f"Forbidden import found in {mod_name}: {line}",
                            )


if __name__ == "__main__":
    unittest.main()
