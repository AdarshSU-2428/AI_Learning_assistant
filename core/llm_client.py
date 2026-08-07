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

        fallback_models = [self.model, "llama-3.2-3b-preview", "llama-3.2-1b-preview", "qwen-2.5-coder-32b", "llama-3.3-70b-versatile"]
        seen_models = set()

        for current_model in fallback_models:
            if current_model in seen_models:
                continue
            seen_models.add(current_model)

            try:
                self.logger.info(f"Attempting response generation with model: {current_model}")
                response = self.client.chat.completions.create(
                    model=current_model,
                    messages=messages,
                    temperature=LLM_TEMPERATURE,
                    max_completion_tokens=LLM_MAX_TOKENS,
                )

                answer = response.choices[0].message.content
                self.logger.info(f"LLM response generated successfully with model: {current_model}")
                return answer

            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "rate_limit" in err_str or "decommissioned" in err_str or "400" in err_str:
                    self.logger.warning(f"Model {current_model} unavailable or rate-limited ({e}). Trying next fallback model...")
                    continue
                else:
                    self.logger.exception(f"Failed to generate response from LLM using {current_model}.")
                    raise

        raise RuntimeError("All LLM models exhausted due to rate limits.")
    