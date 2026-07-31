from pathlib import Path

from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise EnvironmentError(
        "GROQ_API_KEY environment variable is not set."
    )

LLM_MODEL = "llama-3.3-70b-versatile"
LLM_TEMPERATURE = 0.2
LLM_MAX_TOKENS = 1024

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

PDF_SLIDE_WINDOW_SIZE = 3

RETRIEVAL_TOP_K = 35
RERANK_TOP_K = 5
RERANK_SCORE_THRESHOLD = 0.35

EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DOCUMENTS_PATH = PROJECT_ROOT / "data" / "raw"

VECTOR_DB_PATH = PROJECT_ROOT / "data" / "vector_store"
COLLECTION_NAME = "learning_assistant"

KNOWLEDGE_BASE_PATH = PROJECT_ROOT / "knowledge_base"


