from utils.logger import get_logger
from langchain_core.documents import Document


class PromptBuilder:
    def __init__(self):
        self.logger = get_logger(__name__)

    def build_messages(self, system_prompt, user_prompt, user_input, documents):
        self.logger.info("Building messages...")

        try:
            if not isinstance(documents, list):
                raise TypeError("Documents must be a list.")

            if not isinstance(system_prompt, str):
                raise TypeError("System prompt must be a string.")

            if not isinstance(user_prompt, str):
                raise TypeError("User prompt must be a string.")

            context = self._build_context(documents)

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

    def _build_context(self, documents):

        if not documents:
            self.logger.warning("No context documents received.")
            return ""

        context_parts = []

        for index, document in enumerate(documents, start=1):
            if not isinstance(document, Document):
                raise TypeError(f"Item at index {index} is not a LangChain Document.")

            metadata = document.metadata or {}

            source = (
                metadata.get("file_name") or
                (metadata.get("file_path") or metadata.get("source") or "")
                .replace("\\", "/")
                .split("/")[-1] or
                "Unknown"
            )

            page = metadata.get("page")

            document_context = [
                f"Document {index}",
                f"Source : {source}",
            ]

            if page is not None:
                document_context.append(f"Page   : {page}")

            page_content = str(document.page_content) if document.page_content is not None else ""

            document_context.extend([
                "",
                "Content :",
                page_content,
                "-" * 60
            ])

            context_parts.append("\n".join(document_context))

        return "\n\n".join(context_parts)