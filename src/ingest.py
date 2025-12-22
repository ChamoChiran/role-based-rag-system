import os
import json
import logging
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

# Logging setup
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

_ROOT_DATA_DIR_ENV = os.getenv("ROOT_DATA_DIR")
DEFAULT_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
ROOT_DATA_DIR = Path(_ROOT_DATA_DIR_ENV) if _ROOT_DATA_DIR_ENV else DEFAULT_DATA_DIR

def batch_process_all_data(root_dir):
    all_processed_chunks = []

    role_permissions = {
        "finance": ["Finance_Team", "God_Tier_Admins"],
        "marketing": ["Marketing_Team", "God_Tier_Admins"],
        "hr": ["HR_Team", "God_Tier_Admins"],
        "engineering": ["Engineering_Department", "God_Tier_Admins"],
        "general": [
            "Employee_Level",
            "Finance_Team",
            "Marketing_Team",
            "HR_Team",
            "Engineering_Department",
            "God_Tier_Admins",
        ],
    }

    for role_folder in os.listdir(root_dir):
        role_path = os.path.join(root_dir, role_folder)

        if os.path.isdir(role_path) and role_folder in role_permissions:
            chunked_reports_path = os.path.join(role_path, "chunked_reports")

            if os.path.exists(chunked_reports_path):
                logger.info(f"Processing {role_folder} data...")

                for filename in os.listdir(chunked_reports_path):
                    if filename.endswith(".json"):
                        file_path = os.path.join(chunked_reports_path, filename)

                        try:
                            with open(file_path, 'r', encoding='utf-8') as file:
                                data = json.load(file)
                                if not isinstance(data, list):
                                    data = [data]
                        except (json.JSONDecodeError, OSError) as e:
                            logger.error(f"Failed to read JSON {file_path}: {e}")
                            continue

                        for i, item in enumerate(data):
                            raw_lines = item.get("content", [])
                            clean_lines = []


                            for line in raw_lines:
                                s = str(line).strip()
                                if s and s != "```" and "---" not in s:
                                    clean_lines.append(s)

                            content_string = " ".join(clean_lines)

                            if not content_string:
                                headings = [
                                    item.get("section") or "",
                                    item.get("subsection") or "",
                                    item.get("subsubsection") or "",
                                ]
                                content_string = " ".join([h for h in headings if h]).strip()

                            chunk_id = f"{role_folder}_{filename.replace('.json', '')}_{i}"

                            sub = item.get("subsection", "N/A")
                            subsub = item.get("subsubsection", "N/A")

                            if sub != "N/A" and subsub != "N/A":
                                combined_sub = f"{sub} > {subsub}"
                            elif sub != "N/A":
                                combined_sub = sub
                            else:
                                combined_sub = subsub

                            # Build metadata with role flags and a string field for allowed_roles
                            allowed_roles = role_permissions[role_folder]
                            metadata = {
                                "chunk_id": chunk_id,
                                "source": filename,
                                "section": item.get("section", "N/A"),
                                "sub_hierarchy": combined_sub,
                                "allowed_roles": ",".join(allowed_roles),
                                "department": role_folder,
                            }
                            for r in allowed_roles:
                                metadata[f"role_{r}"] = True

                            processed_chunk = {
                                "id": chunk_id,
                                "text": content_string,
                                "metadata": metadata,
                            }

                            all_processed_chunks.append(processed_chunk)
    return all_processed_chunks

def save_to_chromadb(chunks, collection_name="documents"):
    CHROMA_DB_PATH = ROOT_DATA_DIR / "chroma_db"
    CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
    embedder = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    collection = client.get_or_create_collection(name=collection_name, embedding_function=embedder)

    
    cleaned_chunks = []
    for chunk in chunks:
        cleaned_metadata = {k: v for k, v in chunk['metadata'].items() if v is not None}
        cleaned_chunks.append({
            'id': chunk['id'],
            'text': chunk['text'],
            'metadata': cleaned_metadata
        })

    
    documents = [chunk['text'] for chunk in cleaned_chunks]
    metadatas = [chunk['metadata'] for chunk in cleaned_chunks]
    ids = [chunk['id'] for chunk in cleaned_chunks]

    try:
        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    except Exception as e:
        logger.error(f"ChromaDB upsert failed: {e}")
        raise

    return collection

def run_chunking():
    processed_chunks = batch_process_all_data(ROOT_DATA_DIR)
    logger.info(f"Total processed chunks: {len(processed_chunks)}")

    if not processed_chunks:
        logger.warning("No chunks processed. Aborting save.")
        return

    collection = save_to_chromadb(processed_chunks, collection_name="corporate_documents")
    logger.info(f"ChromaDB collection '{collection.name}' now has {collection.count()} documents.")
