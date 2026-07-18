from utils.logger import get_logger
from config.prompts import SYSTEM_PROMPT
from langchain_core.documents import Document


class PromptBuilder:

    def __init__(self):
        self.logger = get_logger(__name__)

    def build_prompt(self, query, documents):
        self.logger.info("Building prompt...")

        try:
            if not isinstance(documents, list):
                raise TypeError("Documents must be a list.")

            context = self._build_context(documents)

            prompt = SYSTEM_PROMPT.format(
                context=context,
                question=query
            )

            self.logger.info("Prompt built successfully.")

            return prompt

        except Exception as e:
            self.logger.error(f"Failed to build prompt: {e}")
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