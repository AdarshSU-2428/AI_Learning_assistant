from utils.logger import get_logger

from groq import Groq

from config.settings import (
    GROQ_API_KEY,
    LLM_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS
)

class LLMClient:
    def __init__(self):
        self.logger = get_logger(__name__)

        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = LLM_MODEL

        self.logger.info(
            "LLM Client initialized successfully "
            f"(Model: {self.model})"
        )

    def _validate_messages(self, messages):
        if not isinstance(messages, list):
            raise TypeError("Messages must be a list.")

        valid_roles = {"system", "user", "assistant"}

        for index, msg in enumerate(messages, start=1):
            if not isinstance(msg, dict):
                raise TypeError(f"Message at index {index} is not a dictionary.")

            if "role" not in msg or "content" not in msg:
                raise ValueError(
                    f"Message at index {index} must contain both 'role' and 'content' keys."
                )

            if not isinstance(msg["role"], str) or not isinstance(msg["content"], str):
                raise TypeError(
                    f"Message at index {index} values for 'role' and 'content' must be strings."
                )

            if msg["role"] not in valid_roles:
                raise ValueError(
                    f"Message at index {index} role '{msg['role']}' is invalid. "
                    f"Allowed roles: {valid_roles}"
                )

            if not msg["role"].strip() or not msg["content"].strip():
                raise ValueError(
                    f"Message at index {index} values for 'role' and 'content' cannot be empty or blank."
                )

    def generate_response(self, messages):
        self._validate_messages(messages)

        self.logger.info("Generating LLM response...")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=LLM_TEMPERATURE,
                max_completion_tokens=LLM_MAX_TOKENS,
            )

            answer = response.choices[0].message.content

            self.logger.info("LLM response generated successfully.")

            return answer

        except Exception as e:
            self.logger.exception("Failed to generate response from LLM.")
            raise
    