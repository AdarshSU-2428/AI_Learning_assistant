from pathlib import Path

from dotenv import load_dotenv
import os

load_dotenv(override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise EnvironmentError(
        "GROQ_API_KEY environment variable is not set."
    )

LLM_MODEL = "qwen/qwen3.8-27b"

CHAT_LLM_MODEL = "qwen/qwen3.8-27b"
QUIZ_LLM_MODEL = "qwen/qwen3.8-27b"
LAB_LLM_MODEL = "qwen/qwen3.8-27b"
EXAM_LLM_MODEL = "qwen/qwen3.8-27b"

LLM_TEMPERATURE = 0.2
LLM_MAX_TOKENS = 2048
LEARNING_MAX_TOKENS = 2048
QUIZ_MAX_TOKENS = 4096
EXAM_MAX_TOKENS = 4096

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

PDF_SLIDE_WINDOW_SIZE = 3

RETRIEVAL_TOP_K = 15
RERANK_TOP_K = 5
RERANK_SCORE_THRESHOLD = 0.35

EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DOCUMENTS_PATH = PROJECT_ROOT / "data" / "raw"

VECTOR_DB_PATH = PROJECT_ROOT / "data" / "vector_store"
COLLECTION_NAME = "learning_assistant"
QUIZ_COLLECTION_NAME = "quiz_bank"
LAB_COLLECTION_NAME = "lab_manual"
EXAM_COLLECTION_NAME = "exam_paper"

QUIZ_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "Quiz"
LAB_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "Lab"
EXAM_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "Exam"

KNOWLEDGE_BASE_PATH = PROJECT_ROOT / "knowledge_base"


