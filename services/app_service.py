from services.chat_service import ChatService
from services.indexing_service import IndexingService


class ApplicationService:

    def __init__(self):
        self.chat_service = ChatService()
        self.indexing_service = IndexingService()

    def index_documents(self, directory_path):
        return self.indexing_service.index_directory(directory_path)

    def chat(self, query):
        return self.chat_service.chat(query)