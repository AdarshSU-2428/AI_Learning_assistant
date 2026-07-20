import re
from utils.logger import get_logger

class ResponseSanitizer:
    _logger = get_logger(__name__)

    @classmethod
    def clean(cls, text):
        if not text:
            cls._logger.warning("Empty response passed to sanitizer.")
            return ""

        cls._logger.info("Sanitizing LLM response...")
      
        cleaned = re.sub(
            r"(?is)<think>.*?(</think>|$)",
            "",
            text
        )

        return cleaned.strip()
