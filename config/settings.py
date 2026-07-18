from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise EnvironmentError(
        "GROQ_API_KEY environment variable is not set."
    )

LLM_MODEL = "qwen/qwen3.6-27b"
LLM_TEMPERATURE = 0.2
LLM_MAX_TOKENS = 1024

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

RETRIEVAL_TOP_K = 20
RERANK_TOP_K = 5

EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

VECTOR_DB_PATH = "data/vector_store"
COLLECTION_NAME = "learning_assistant"

