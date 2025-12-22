"""
Simple retrieval script to query the RAG database.
Usage: python simple_retrieval.py
"""

import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Setup
ROOT_DATA_DIR = Path(os.getenv("ROOT_DATA_DIR", "../data"))
VECTOR_DB_DIR = ROOT_DATA_DIR / "chroma_db"

# Initialize
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

chroma_client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
collection = chroma_client.get_or_create_collection(
    name="corporate_documents",
    embedding_function=embedding_function
)

print(f"Database loaded: {collection.count()} documents")
print("=" * 80)

# Interactive query
while True:
    query = input("\nEnter your query (or 'quit' to exit): ").strip()
    
    if query.lower() in ['quit', 'exit', 'q']:
        print("Goodbye!")
        break
    
    if not query:
        continue
    
    results = collection.query(
        query_texts=[query],
        n_results=3,
        include=["documents", "metadatas", "distances"]
    )
    
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    
    if not documents:
        print("No results found.")
        continue
    
    print(f"\nFound {len(documents)} results:")
    print("-" * 80)
    
    for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances), 1):
        source = meta.get("source", "unknown") if meta else "unknown"
        section = meta.get("section", "N/A") if meta else "N/A"
        department = meta.get("department", "N/A") if meta else "N/A"
        
        print(f"\n[Result {i}] (Distance: {dist:.4f})")
        print(f"Department: {department}")
        print(f"Source: {source}")
        print(f"Section: {section}")
        print(f"Content: {doc[:300]}...")
        print("-" * 80)

