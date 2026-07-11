from pypdf import PdfReader

from core.loaders.loader import BaseLoader 

class PDFLoader(BaseLoader) :
    def extract_text(self) :
        self.logger.info(f"Extracting text from {self.file_path.name}")

        try :
            reader = PdfReader(self.file_path)

            text = ""

            for page in reader.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

            self.logger.info(f"Successfully extracted text from {len(reader.pages)} pages.")

            return text

        except Exception as e :
            self.logger.error(f"Error while reading PDF: {e}")
            raise


