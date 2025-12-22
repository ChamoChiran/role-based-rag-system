import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

ROOT_DATA_DIR = Path(os.getenv("ROOT_DATA_DIR"))
VECTOR_DB_DIR = ROOT_DATA_DIR / "chroma_db"
COLLECTION_NAME = "corporate_documents"

embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

chroma_client = chromadb.PersistentClient(
    path=str(VECTOR_DB_DIR)
)

collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_function
)
