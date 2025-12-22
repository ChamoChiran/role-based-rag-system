"""
Role-Based Retrieval Test Script
Tests the RAG database with different user roles to verify access control.
"""

import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path
import os
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv()

# Role definitions from ingest.py
AVAILABLE_ROLES = [
    "Employee_Level",
    "Finance_Team",
    "Marketing_Team",
    "HR_Team",
    "Engineering_Department",
    "God_Tier_Admins"
]

ROLE_DESCRIPTIONS = {
    "Employee_Level": "Basic employee - access to general documents only",
    "Finance_Team": "Finance department - access to general + finance documents",
    "Marketing_Team": "Marketing department - access to general + marketing documents",
    "HR_Team": "HR department - access to general + HR documents",
    "Engineering_Department": "Engineering department - access to general + engineering documents",
    "God_Tier_Admins": "Admin - access to ALL departments",
}

# Setup paths
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

def retrieve_by_role(query: str, role: str, n_results: int = 5) -> List[Dict[str, Any]]:
    """Retrieve documents filtered by role permissions."""

    # Fetch more results than needed to filter by role
    fetch_count = n_results * 5

    results = collection.query(
        query_texts=[query],
        n_results=fetch_count,
        include=["documents", "metadatas", "distances"]
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    ids = results.get("ids", [[]])[0]

    filtered_results = []
    role_flag = f"role_{role}"

    for doc, meta, dist, doc_id in zip(documents, metadatas, distances, ids):
        # Check if user has access
        if meta and meta.get(role_flag, False):
            filtered_results.append({
                "id": doc_id,
                "document": doc,
                "metadata": meta,
                "distance": dist,
                "department": meta.get("department", "unknown"),
                "source": meta.get("source", "unknown"),
                "section": meta.get("section", "N/A"),
            })

            if len(filtered_results) >= n_results:
                break

    return filtered_results

def test_role_access():
    """Test different roles with various queries."""

    print("=" * 80)
    print("ROLE-BASED RETRIEVAL ACCESS CONTROL TEST")
    print("=" * 80)
    print(f"\nDatabase: {VECTOR_DB_DIR}")
    print(f"Collection: {collection.name}")
    print(f"Total Documents: {collection.count()}\n")

    # Test queries for different departments
    test_cases = [
        {
            "query": "What are the quarterly financial results?",
            "expected_access": ["Finance_Team", "God_Tier_Admins"],
            "denied_access": ["Employee_Level", "Marketing_Team", "HR_Team", "Engineering_Department"]
        },
        {
            "query": "What are the marketing strategies for Q4?",
            "expected_access": ["Marketing_Team", "God_Tier_Admins"],
            "denied_access": ["Employee_Level", "Finance_Team", "HR_Team", "Engineering_Department"]
        },
        {
            "query": "What is the employee handbook?",
            "expected_access": ["Employee_Level", "Finance_Team", "Marketing_Team", "HR_Team", "Engineering_Department", "God_Tier_Admins"],
            "denied_access": []
        }
    ]

    for test_idx, test_case in enumerate(test_cases, 1):
        query = test_case["query"]

        print(f"\n{'='*80}")
        print(f"TEST CASE {test_idx}: {query}")
        print(f"{'='*80}\n")

        for role in AVAILABLE_ROLES:
            results = retrieve_by_role(query, role, n_results=3)

            # Determine expected result
            should_have_access = role in test_case["expected_access"]
            has_results = len(results) > 0

            # Status indicator
            if should_have_access and has_results:
                status = "✓ PASS"
            elif not should_have_access and not has_results:
                status = "✓ PASS"
            elif should_have_access and not has_results:
                status = "✗ FAIL (expected access)"
            else:
                status = "⚠ WARN (unexpected access)"

            print(f"{status} | {role:25} | {len(results)} results")

            if results and should_have_access:
                for idx, r in enumerate(results[:2], 1):  # Show first 2 results
                    print(f"         └─ [{idx}] Dept: {r['department']:12} Source: {r['source']}")

        print()

def interactive_role_based_query():
    """Interactive mode for testing role-based queries."""

    print("\n" + "=" * 80)
    print("INTERACTIVE ROLE-BASED QUERY MODE")
    print("=" * 80)
    print("\nAvailable Roles:")
    for idx, (role, desc) in enumerate(ROLE_DESCRIPTIONS.items(), 1):
        print(f"  {idx}. {role:25} - {desc}")

    while True:
        print("\n" + "-" * 80)

        # Select role
        role_input = input("\nSelect role number (1-6) or 'q' to quit: ").strip()
        if role_input.lower() in ['q', 'quit', 'exit']:
            print("Exiting interactive mode.")
            break

        try:
            role_idx = int(role_input) - 1
            if role_idx < 0 or role_idx >= len(AVAILABLE_ROLES):
                print("Invalid role number. Please try again.")
                continue
            selected_role = AVAILABLE_ROLES[role_idx]
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        # Get query
        query = input(f"\nEnter query as '{selected_role}': ").strip()
        if not query:
            continue

        # Retrieve and display results
        print(f"\n{'='*80}")
        print(f"Role: {selected_role}")
        print(f"Query: {query}")
        print(f"{'='*80}")

        results = retrieve_by_role(query, selected_role, n_results=5)

        if not results:
            print(f"\n❌ No accessible documents for role '{selected_role}'")
            print(f"   This role may not have permission to access relevant documents.")
        else:
            print(f"\n✓ Found {len(results)} accessible documents:\n")

            for idx, r in enumerate(results, 1):
                print(f"[{idx}] Department: {r['department']}")
                print(f"    Source: {r['source']}")
                print(f"    Section: {r['section']}")
                print(f"    Distance: {r['distance']:.4f}")
                print(f"    Content: {r['document'][:200]}...")
                print()

if __name__ == "__main__":
    # Run automated tests
    test_role_access()

    # Ask if user wants interactive mode
    print("\n" + "=" * 80)
    response = input("Run interactive mode? (y/n): ").strip().lower()
    if response in ['y', 'yes']:
        interactive_role_based_query()
    else:
        print("Done!")

