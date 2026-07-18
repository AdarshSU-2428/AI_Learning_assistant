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

    def _validate_prompt(self, prompt):
        if not isinstance(prompt, str):
            raise TypeError("Prompt must be a string.")

        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

    def generate_response(self, prompt):
        self._validate_prompt(prompt)

        self.logger.info("Generating LLM response...")

        try:
            response = self.client.chat.completions.create(
                model=self.model,

                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                temperature=LLM_TEMPERATURE,
                max_completion_tokens=LLM_MAX_TOKENS,
            )

            answer = response.choices[0].message.content

            self.logger.info("LLM response generated successfully.")

            return answer

        except Exception:

            self.logger.exception(
                "Failed to generate response from LLM."
            )
 

    