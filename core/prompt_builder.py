from utils.logger import get_logger
from core.context_builder import ContextBuilder


class PromptBuilder:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.context_builder = ContextBuilder()

    def build_messages(self, system_prompt, user_prompt, user_input, documents, subject=None):
        self.logger.info("Building messages...")

        try:
            if not isinstance(documents, list):
                raise TypeError("Documents must be a list.")

            if not isinstance(system_prompt, str):
                raise TypeError("System prompt must be a string.")

            if not isinstance(user_prompt, str):
                raise TypeError("User prompt must be a string.")

            context = self.context_builder.build_context(documents)

            formatted_system_prompt = system_prompt
            if subject and isinstance(subject, str) and subject.strip():
                clean_subj = subject.strip()
                subject_instruction = (
                    f"\n\nCURRENT COURSE SUBJECT SCOPE:\n"
                    f"The user has selected the course subject: '{clean_subj}'.\n"
                    f"- Answer questions using the retrieved materials and concepts relevant to '{clean_subj}'.\n"
                    f"- For programming and algorithm courses (such as DAA, OS, AI), you are free to provide implementations in requested programming languages (like C, C++, Python, or Java).\n"
                    f"- If the question asks about a completely unrelated course domain (such as asking about Biology while in Python, or asking about SQL database tables while in Digital Electronics), politely guide the user to select the appropriate course subject from the sidebar."
                )
                formatted_system_prompt = formatted_system_prompt + subject_instruction

            user_content = user_prompt.format(
                context=context,
                question=user_input
            )

            if subject and isinstance(subject, str) and subject.strip():
                user_content = f"[Selected Course Subject: {subject.strip()}]\n\n" + user_content

            messages = [
                {
                    "role": "system",
                    "content": formatted_system_prompt
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