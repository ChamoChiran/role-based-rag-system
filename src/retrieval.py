# python
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Role definitions matching ingest.py
ROLE_HIERARCHY = {
    "Employee_Level": ["general"],
    "Finance_Team": ["general", "finance"],
    "Marketing_Team": ["general", "marketing"],
    "HR_Team": ["general", "hr"],
    "Engineering_Department": ["general", "engineering"],
    "God_Tier_Admins": ["general", "finance", "marketing", "hr", "engineering"],
}

# Setup paths
_ROOT_DATA_DIR_ENV = os.getenv("ROOT_DATA_DIR")
DEFAULT_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
ROOT_DATA_DIR = Path(_ROOT_DATA_DIR_ENV) if _ROOT_DATA_DIR_ENV else DEFAULT_DATA_DIR
CHROMA_DB_PATH = ROOT_DATA_DIR / "chroma_db"

ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

def _client():
    return chromadb.PersistentClient(path=str(CHROMA_DB_PATH))

def retrieve_docs(user_query: str, user_role: str, n_results: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieve documents based on user query and role-based access control.

    Args:
        user_query: The search query
        user_role: User's role (e.g., "Finance_Team", "Employee_Level", "God_Tier_Admins")
        n_results: Maximum number of results to return (will fetch more to filter by role)

    Returns:
        List of documents accessible to the user's role
    """
    collection = _client().get_or_create_collection(
        name="corporate_documents",
        embedding_function=ef,
    )

    # Fetch more results than needed since we'll filter by role
    fetch_count = n_results * 3

    res = collection.query(
        query_texts=[user_query],
        n_results=fetch_count,
        include=["documents", "metadatas", "distances"],
    )

    results = []
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    ids = res.get("ids", [[]])[0]
    dists = res.get("distances", [[]])[0] if "distances" in res else [None] * len(docs)

    # Filter results based on role permissions
    for i in range(len(docs)):
        meta = metas[i] or {}

        # Check if user has access to this document
        role_flag = f"role_{user_role}"
        has_access = meta.get(role_flag, False)

        if has_access:
            results.append({
                "id": ids[i],
                "document": docs[i],
                "source": meta.get("source"),
                "section": meta.get("section"),
                "sub_hierarchy": meta.get("sub_hierarchy"),
                "department": meta.get("department"),
                "distance": dists[i],
                "allowed_roles": meta.get("allowed_roles", ""),
            })

            # Stop when we have enough results
            if len(results) >= n_results:
                break

    return results

if __name__ == "__main__":
    print("=" * 80)
    print("Role-Based Retrieval Test")
    print("=" * 80)

    query = "What are the quarterly financial results?"

    # Test different roles
    test_roles = [
        "Employee_Level",
        "Finance_Team",
        "Marketing_Team",
        "God_Tier_Admins"
    ]

    for role in test_roles:
        print(f"\n{'='*80}")
        print(f"Testing Role: {role}")
        print(f"Query: {query}")
        print(f"{'='*80}")

        results = retrieve_docs(query, role, n_results=5)

        if not results:
            print(f"❌ No accessible documents for {role}")
        else:
            print(f"✓ Found {len(results)} accessible documents for {role}\n")

            for idx, r in enumerate(results, 1):
                print(f"[{idx}] ID: {r['id']}")
                print(f"    Department: {r['department']}")
                print(f"    Source: {r['source']}")
                print(f"    Section: {r['section']}")
                print(f"    Distance: {r['distance']:.4f}")
                print(f"    Allowed Roles: {r['allowed_roles']}")
                print(f"    Content: {r['document'][:150]}...")
                print()

