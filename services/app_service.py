from services.learning_service import LearningService
from services.indexing_service import IndexingService


class ApplicationService:

    def __init__(self):
        self.learning_service = LearningService()
        self.indexing_service = IndexingService()

    def index_documents(self, directory_path):
        return self.indexing_service.index_directory(directory_path)

    def chat(self, query, subject=None):
        return self.learning_service.chat(query, subject=subject)