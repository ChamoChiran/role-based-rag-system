"""
Test script for RAGService with role-based access control
"""

import sys
from pathlib import Path

# Add app directory to path
app_dir = Path(__file__).resolve().parent.parent / "app"
sys.path.insert(0, str(app_dir.parent))

from app.services.rag_service import RAGService
from app.utils.vector_store import collection

# Available roles
AVAILABLE_ROLES = [
    "Employee_Level",
    "Finance_Team",
    "Marketing_Team",
    "HR_Team",
    "Engineering_Department",
    "God_Tier_Admins"
]

def test_rag_service():
    """Test RAGService with different roles and queries"""

    print("=" * 80)
    print("RAG SERVICE ROLE-BASED RETRIEVAL TEST")
    print("=" * 80)
    print(f"\nTotal Documents in Collection: {collection.count()}\n")

    # Initialize RAGService
    rag_service = RAGService(vector_store=None)

    # Test cases
    test_queries = [
        "What are the quarterly financial results?",
        "Tell me about marketing strategies",
        "What is the employee handbook?",
        "Engineering best practices"
    ]

    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"Query: {query}")
        print(f"{'='*80}\n")

        for role in AVAILABLE_ROLES:
            context, sources = rag_service.answer(role, query, n_results=3)

            # Check if access was granted
            has_access = not context.startswith("No accessible")

            status = "✓" if has_access else "✗"
            source_str = f" | Sources: {', '.join(sources)}" if sources else ""

            print(f"{status} {role:25} {source_str}")

            if has_access:
                # Show first 100 chars of context
                preview = context[:100].replace('\n', ' ') + "..."
                print(f"  Preview: {preview}")

        print()

def interactive_rag_test():
    """Interactive test of RAGService"""

    print("\n" + "=" * 80)
    print("INTERACTIVE RAG SERVICE TEST")
    print("=" * 80)
    print("\nAvailable Roles:")
    for idx, role in enumerate(AVAILABLE_ROLES, 1):
        print(f"  {idx}. {role}")

    rag_service = RAGService(vector_store=None)

    while True:
        print("\n" + "-" * 80)

        # Get role
        role_input = input("\nSelect role (1-6) or 'q' to quit: ").strip()
        if role_input.lower() in ['q', 'quit']:
            break

        try:
            role_idx = int(role_input) - 1
            if role_idx < 0 or role_idx >= len(AVAILABLE_ROLES):
                print("Invalid role number")
                continue
            role = AVAILABLE_ROLES[role_idx]
        except ValueError:
            print("Invalid input")
            continue

        # Get query
        query = input(f"\nEnter query as {role}: ").strip()
        if not query:
            continue

        # Get answer
        print(f"\n{'='*80}")
        print(f"Role: {role}")
        print(f"Query: {query}")
        print(f"{'='*80}\n")

        context, sources = rag_service.answer(role, query, n_results=5)

        print("Retrieved Context:")
        print("-" * 80)
        print(context[:500] + "..." if len(context) > 500 else context)
        print("-" * 80)
        print(f"\nSources: {', '.join(sources) if sources else 'None'}")

        # Generate answer
        context_list = context.split("\n\n") if context else []
        answer = rag_service.generate_answer(context_list, query)
        print(f"\nGenerated Answer:")
        print("-" * 80)
        print(answer[:500] + "..." if len(answer) > 500 else answer)

if __name__ == "__main__":
    # Run automated tests
    test_rag_service()

    # Ask for interactive mode
    print("\n" + "=" * 80)
    response = input("Run interactive mode? (y/n): ").strip().lower()
    if response in ['y', 'yes']:
        interactive_rag_test()
    else:
        print("Done!")

