from app.utils.vector_store import collection
from typing import List, Dict, Any, Tuple


class RAGService:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def answer(self, role: str, query: str, n_results: int = 5) -> Tuple[str, List[str]]:
        """
        Answer a query based on the user's role using the vector store with role-based access control.

        :param role: Role of the user making the query (e.g., "Finance_Team", "Employee_Level")
        :param query: The user's query
        :param n_results: Number of results to return
        :return: Tuple of (context_text, list of sources)
        """
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

        if not documents:
            return (
                "No information found for this query.",
                []
            )

        # Filter results based on role permissions
        context_chunks = []
        sources = []
        role_flag = f"role_{role}"

        MAX_DISTANCE = 0.5

        for doc, meta, dist in zip(documents, metadatas, distances):
            if MAX_DISTANCE < dist:
                continue
            # Check if user has access to this document
            has_access = meta and meta.get(role_flag, False)

            if has_access:
                context_chunks.append(doc)
                source = meta.get("source", "unknown")
                if source not in sources:
                    sources.append(source)

                # Stop when we have enough results
                if len(context_chunks) >= n_results:
                    break

        # Check if any accessible documents were found
        if not context_chunks:
            return (
                f"No accessible information found for role '{role}' regarding this query.",
                []
            )

        context_text = "\n\n".join(context_chunks)

        return context_text, sources


    def generate_answer(self, documents: List[str], query: str) -> str:
        """
        Generate an answer based on retrieved documents and the original query.

        :param documents: List of retrieved document chunks
        :param query: The user's original query
        :return: Generated answer
        """
        if not documents:
            return "No documents available to generate an answer."

        # Combine all document content
        combined_content = " ".join(documents)

        # Placeholder for answer generation logic
        # In a real implementation, this could involve using a language model (e.g., LLM)
        # For now, return a simple formatted response
        answer = f"Based on your query '{query}', here is the relevant information:\n\n{combined_content}"

        return answer

