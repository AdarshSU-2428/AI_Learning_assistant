from langchain_core.documents import Document
from utils.logger import get_logger

class ContextBuilder:
    def __init__(self):
        self.logger = get_logger(__name__)

    def build_context(self, documents):
        self.logger.info("Building consolidated context from accepted evidence documents...")

        try:
            if not documents:
                self.logger.warning("No context documents received.")
                return ""

            if not isinstance(documents, list):
                raise TypeError("Documents must be a list of LangChain Document objects.")

            context_parts = []
            seen_contents = set()

            for index, doc in enumerate(documents, start=1):
                if not isinstance(doc, Document):
                    raise TypeError(f"Item at index {index} is not a LangChain Document.")

                page_content = str(doc.page_content).strip() if doc.page_content is not None else ""
                metadata = doc.metadata or {}

                source = (
                    metadata.get("file_name") or
                    (metadata.get("file_path") or metadata.get("source") or "")
                    .replace("\\", "/")
                    .split("/")[-1] or
                    "Unknown"
                )

                page = metadata.get("page")
                slide = metadata.get("slide")

                doc_key = str(doc.page_content).strip() if doc.page_content is not None else ""
                if doc_key in seen_contents:
                    continue

                seen_contents.add(doc_key)

                document_context = [
                    f"Document {len(context_parts) + 1}",
                    f"Source : {source}",
                ]

                if page is not None:
                    document_context.append(f"Page   : {page}")

                if slide is not None:
                    document_context.append(f"Slide  : {slide}")

                document_context.extend([
                    "",
                    "Content :",
                    page_content,
                    "-" * 60
                ])

                context_parts.append("\n".join(document_context))

            self.logger.info(f"Built context successfully with {len(context_parts)} unique document chunks.")
            final_context = "\n\n".join(context_parts)
            if len(final_context) > 8000:
                final_context = final_context[:8000] + "\n...[Context truncated to fit token limits]..."
            return final_context

        except Exception as e:
            self.logger.error(f"Failed to build context: {e}")
            raise