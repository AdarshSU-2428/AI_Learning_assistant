from services.learning_service import LearningService
from services.indexing_service import IndexingService
from services.quiz_service import QuizService
from services.lab_service import LabService


class ApplicationService:

    def __init__(self):
        self.learning_service = LearningService()
        self.indexing_service = IndexingService()
        self.quiz_service = QuizService()
        self.lab_service = LabService()

    def index_documents(self, directory_path):
        notes_res = self.indexing_service.index_directory(directory_path)
        quiz_res = self.indexing_service.index_quiz_directory()
        lab_res = self.indexing_service.index_lab_directory()
        return {"notes": notes_res, "quiz": quiz_res, "lab": lab_res}

    def chat(self, query, subject=None):
        return self.learning_service.chat(query, subject=subject)

    def lab_chat(self, query, subject=None):
        return self.lab_service.chat(query, subject=subject)
    
    def generate_quiz(self, topic, subject=None, num_questions=None, difficulty=None):
        return self.quiz_service.generate_quiz(
            topic=topic,
            subject=subject,
            num_questions=num_questions,
            difficulty=difficulty
        )

    def evaluate_quiz_submission(self, quiz_questions, user_answers):
        return self.quiz_service.evaluate_submission(
            quiz_questions=quiz_questions,
            user_answers=user_answers
        )