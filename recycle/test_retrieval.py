"""
Simple test script to verify ChromaDB setup and retrieval functionality.
Run this script to test if the vector database is working correctly.
"""

import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup paths
ROOT_DATA_DIR = Path(os.getenv("ROOT_DATA_DIR", "../data"))
VECTOR_DB_DIR = ROOT_DATA_DIR / "chroma_db"
COLLECTION_NAME = "corporate_documents"

print("=" * 80)
print("RAG Database Retrieval Test")
print("=" * 80)
print(f"\nDatabase Path: {VECTOR_DB_DIR}")
print(f"Collection Name: {COLLECTION_NAME}")

# Initialize embedding function
print("\n[1/4] Loading embedding model...")
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
print("✓ Embedding model loaded successfully")

# Connect to ChromaDB
print("\n[2/4] Connecting to ChromaDB...")
try:
    chroma_client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
    print("✓ Connected to ChromaDB successfully")
except Exception as e:
    print(f"✗ Error connecting to ChromaDB: {e}")
    exit(1)

# Get collection
print("\n[3/4] Accessing collection...")
try:
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function
    )

    # Get collection stats
    count = collection.count()
    print(f"✓ Collection '{COLLECTION_NAME}' accessed successfully")
    print(f"  Total documents in collection: {count}")

    if count == 0:
        print("\n⚠ Warning: Collection is empty. Please run the ingestion process first.")
        exit(0)

except Exception as e:
    print(f"✗ Error accessing collection: {e}")
    exit(1)

# Test retrieval
print("\n[4/4] Testing retrieval with sample queries...")
print("-" * 80)

test_queries = [
    "What are the company policies on remote work?",
    "Tell me about the quarterly financial results",
    "What are the marketing strategies for Q4?",
    "What is the employee handbook about?",
]

for idx, query in enumerate(test_queries, 1):
    print(f"\nQuery {idx}: {query}")
    print("-" * 40)

    try:
        results = collection.query(
            query_texts=[query],
            n_results=3,
            include=["documents", "metadatas", "distances"]
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        if not documents:
            print("  No results found")
            continue

        for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances), 1):
            source = meta.get("source", "unknown") if meta else "unknown"
            section = meta.get("section", "N/A") if meta else "N/A"

            print(f"\n  Result {i}:")
            print(f"    Source: {source}")
            print(f"    Section: {section}")
            print(f"    Distance: {dist:.4f}")
            print(f"    Content Preview: {doc[:150]}...")

    except Exception as e:
        print(f"  ✗ Error during retrieval: {e}")

print("\n" + "=" * 80)
print("Test Complete!")
print("=" * 80)

