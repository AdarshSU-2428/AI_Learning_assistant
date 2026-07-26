from pypdf import PdfReader

from core.loaders.loader import BaseLoader


class PDFLoader(BaseLoader):
    def extract_text(self):
        self.logger.info(f"Extracting text from {self.file_path.name}")

        try:
            reader = PdfReader(self.file_path)

            units = []

            for page_num, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text()

                if page_text and page_text.strip():
                    units.append(
                        {
                            "text": page_text,
                            "metadata": {"page": page_num},
                        }
                    )

            self.logger.info(f"Successfully extracted text from {len(reader.pages)} pages.")

            return units

        except Exception as e:
            self.logger.error(f"Error while reading PDF: {e}")
            raise
