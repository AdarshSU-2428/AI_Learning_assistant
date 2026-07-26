from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from utils.logger import get_logger
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP


class Chunker:
    def __init__(self, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
        self.logger = get_logger(__name__)

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        )

    def chunk_text(self, text, metadata, start_chunk_id=0):
        self.logger.info("Starting text chunking...")

        try:
            if not isinstance(text, str):
                raise TypeError("Input text must be a string.")

            if metadata is None:
                metadata = {}
            else:
                metadata = dict(metadata)

            document = Document(page_content=text, metadata=metadata)

            chunks = self.text_splitter.split_documents([document])

            for index, chunk in enumerate(chunks):
                chunk.metadata["chunk_id"] = start_chunk_id + index

            self.logger.info(f"Text chunked successfully into {len(chunks)} chunks.")
            return chunks

        except Exception as e:
            self.logger.error(f"Error during text chunking: {e}")
            raise
