import re
from utils.logger import get_logger


class SafetyManager:
    def __init__(self):
        self.logger = get_logger(__name__)
        
        self.injection_patterns = [
            r"(?i)\bignore\s+previous\s+instructions\b",
            r"(?i)\bignore\s+above\s+instructions\b",
            r"(?i)\bforget\s+all\s+(?:prior|previous)\s+instructions\b",
            r"(?i)\bdisregard\s+(?:all\s+)?previous\s+instructions\b",
            r"(?i)\breveal\s+(?:your\s+)?system\s+prompt\b",
            r"(?i)\breveal\s+(?:your\s+)?prompt\b",
            r"(?i)\bdecode\s+(?:the\s+)?system\s+prompt\b",
            r"(?i)\bprint\s+(?:your\s+)?system\s+prompt\b",
            r"(?i)\bshow\s+(?:your\s+)?system\s+prompt\b",
            r"(?i)\boutput\s+(?:your\s+)?system\s+prompt\b",
            r"(?i)\byou\s+are\s+now\s+in\s+developer\s+mode\b",
            r"(?i)\bact\s+as\s+an\s+unfiltered\b"
        ]

    def sanitize_input(self, text):
        self.logger.info("Sanitizing input text for potential prompt injection...")

        if not text or not isinstance(text, str):
            raise ValueError("Input text must be a non-empty string.")

        sanitized = text
        for pattern in self.injection_patterns:
            sanitized = re.sub(pattern, "", sanitized)

        sanitized = sanitized.lstrip(" .!?,-_")
        sanitized = sanitized.rstrip(" .,-_")

        if not sanitized.strip():
            self.logger.warning("Input text was empty after sanitization.")
            raise ValueError("Question was empty after sanitization.")

        return sanitized

    def sanitize_output(self, response_text):
        self.logger.info("Sanitizing LLM response output...")

        if not response_text or not isinstance(response_text, str):
            self.logger.warning("Empty response passed to sanitizer.")
            return ""

        cleaned = re.sub(
            r"(?is)<think>.*?(</think>|$)",
            "",
            response_text
        )

        return cleaned.strip()
