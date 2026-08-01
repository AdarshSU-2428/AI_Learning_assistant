from pypdf import PdfReader

from core.loaders.loader import BaseLoader
from core.metadata import create_document_metadata
from config.settings import PDF_SLIDE_WINDOW_SIZE


class PDFLoader(BaseLoader):
    def __init__(self, file_path=None, window_size=PDF_SLIDE_WINDOW_SIZE):
        super().__init__(file_path)
        self.window_size = window_size

    def extract_text(self):
        self.logger.info(f"Extracting text from {self.file_path.name}")

        try:
            reader = PdfReader(self.file_path)
            raw_pages = []

            subject, content_type, source_type = self.infer_metadata_attributes()

            for page_num, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    raw_pages.append((page_num, page_text.strip()))

            units = []
            if not raw_pages:
                return units

            total_words = sum(len(txt.split()) for _, txt in raw_pages)
            avg_words = total_words / len(raw_pages) if raw_pages else 0

            if avg_words < 150 and len(raw_pages) > 1:
                for i in range(len(raw_pages)):
                    window = raw_pages[i : i + self.window_size]
                    combined_text = "\n\n".join(
                        f"[Slide {p}]:\n{txt}" for p, txt in window
                    )
                    start_p = window[0][0]
                    end_p = window[-1][0]
                    page_meta = (
                        start_p if start_p == end_p else f"{start_p}-{end_p}"
                    )

                    meta = create_document_metadata(
                        file_name=self.file_path.name,
                        file_path=str(self.file_path),
                        page=page_meta,
                        slide=page_meta,
                        subject=subject,
                        content_type=content_type,
                        source_type=source_type
                    )

                    units.append(
                        {
                            "text": combined_text,
                            "metadata": meta,
                        }
                    )
            else:
                for page_num, page_text in raw_pages:
                    meta = create_document_metadata(
                        file_name=self.file_path.name,
                        file_path=str(self.file_path),
                        page=page_num,
                        subject=subject,
                        content_type=content_type,
                        source_type=source_type
                    )

                    units.append(
                        {
                            "text": page_text,
                            "metadata": meta,
                        }
                    )

            self.logger.info(f"Successfully extracted {len(units)} units from {len(reader.pages)} pages (subject: {subject}, content_type: {content_type}, source_type: {source_type}, avg words/page: {avg_words:.1f}).")

            return units

        except Exception as e:
            self.logger.error(f"Error while reading PDF: {e}")
            raise
