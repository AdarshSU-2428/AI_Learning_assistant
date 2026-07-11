from docx import Document

from core.loaders.loader import BaseLoader

class DOCXLoader(BaseLoader):
    def extract_text(self) :
        self.logger.info(f"Extracting text from {self.file_path.name}")

        try :
            document = Document(self.file_path)

            text = ""

            for paragraph in document.paragraphs :
                if paragraph.text.strip():
                    text += paragraph.text + "\n"

            for table in document.tables :
                text += "\n"
                for row in table.rows :
                    row_text = []
                    for cell in row.cells:
                        row_text.append(cell.text.strip())

                    text += " | ".join(row_text) + "\n"

            self.logger.info("Successfully extracted text from DOCX.")

            return text

        except Exception as e:
            self.logger.error(f"Error while loading DOCX : {e}")
            raise