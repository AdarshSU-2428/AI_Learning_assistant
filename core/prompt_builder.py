from utils.logger import get_logger
from core.context_builder import ContextBuilder


class PromptBuilder:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.context_builder = ContextBuilder()

    def build_messages(self, system_prompt, user_prompt, user_input, documents):
        self.logger.info("Building messages...")

        try:
            if not isinstance(documents, list):
                raise TypeError("Documents must be a list.")

            if not isinstance(system_prompt, str):
                raise TypeError("System prompt must be a string.")

            if not isinstance(user_prompt, str):
                raise TypeError("User prompt must be a string.")

            context = self.context_builder.build_context(documents)

            user_content = user_prompt.format(
                context=context,
                question=user_input
            )

            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_content
                }
            ]

            self.logger.info("Messages built successfully.")

            return messages

        except Exception as e:
            self.logger.error(f"Failed to build messages: {e}")
            raise