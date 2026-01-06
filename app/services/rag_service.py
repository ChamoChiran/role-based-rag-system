from typing import List, Dict, Any, Tuple
import re
from app.utils.vector_store import collection
from app.utils.llm import LLMClient


def _clean_and_dedpe_docs(documents: List[str]) -> List[str]:
    # use sets for O(n) searching - optimizations
    seen = set()
    cleaned = []

    for doc in documents:
        if not doc:
            continue

        # normalize characters
        normalized_doc = re.sub(r"\s+", " ", doc).strip()

        # skip tiny or duplicate chunks
        if len(normalized_doc) < 20:
            continue
        if normalized_doc in seen:
            continue

        seen.add(normalized_doc)
        cleaned.append(normalized_doc)

    return cleaned


def _build_bounded_context(documents: List[str], max_chars: int) -> str:
    """
    Combine docs into a single context string without exceeding max_chars.
    :param documents:
    :param max_chars:
    :return:
    """

    parts = []
    total = 0

    for i, doc in enumerate(documents, start=1):
        chunk = f"[Chunk {i}]\n{doc}\n"

        if total + len(chunk) > max_chars:
            break

        parts.append(chunk)
        total += len(chunk)

    return "\n".join(parts).strip()


def _prompt_engineering(context: str, query: str) -> str:
    """
    Prompt engineering to guide the LLM in generating accurate answers.
    :param context:
    :param query:
    :return:
    """

    return f"""
    You are a retrieval-augmented assistant.
    
    RULES (must follow):
    - Use ONLY the information in the provided CONTEXT.
    - If the context does not contain the answer, say exactly:
      "I don't have enough information in the provided documents."
    - Do NOT guess. Do NOT add outside facts.
    - Format the answer using clear Markdown structure.
    - Use bullet points for lists, components, features, or multiple items.
    - Avoid long paragraphs when listing information.
    - Use headings and bullet points instead of inline sentences.
    - Use GitHub-flavored Markdown only.
    
    CONTEXT:
    {context}
    
    QUESTION:
    {query}
    
    ANSWER:
    """.strip()


def _tokenize(text: str) -> set:
    """
    Basic tokenizer into lowercase word set.
    """
    words = re.findall(r"[a-zA-Z0-9_]+", (text or "").lower())
    return set(words)


class RAGService:
    def __init__(self, vector_store, llm):
        self.vector_store = vector_store
        self.llm = llm

    def answer(self, role: str, query: str, n_results: int = 5) -> Tuple[str, List[str], List[str]]:
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
                [], []
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
                [], []
            )

        context_text = "\n\n".join(context_chunks)

        return context_text, sources, context_chunks

    def generate_answer(self, documents: List[str], query: str) -> str:
        """
        Generate an answer based on retrieved documents and the original query.

        :param documents: List of retrieved document chunks
        :param query: The user's original query
        :return: Generated answer
        """
        if not documents:
            return "No documents available to generate an answer."

        cleaned_docs = _clean_and_dedpe_docs(documents)
        context = _build_bounded_context(cleaned_docs, max_chars=12000)

        if self.llm is None:
            return self._extractive_fallback_answer(cleaned_docs, query)

        prompt = _prompt_engineering(context=context, query=query)

        try:
            return self.llm(prompt)
        except Exception as e:
            fallback = self._extractive_fallback_answer(cleaned_docs, query)
            return f"Error generating answer with LLM: {str(e)}\n\nFallback: {fallback}"

    def _extractive_fallback_answer(self, documents: List[str], query: str) -> str:
        """
        Simple extractive fallback answer by returning the most relevant document chunk.
        :param documents:
        :param query:
        :return:
        """

        query_terms = _tokenize(query)
        if not query_terms:
            extracts  = "\n\n".join(documents[:2])
            return f"Relevant extracts from documents:\n\n{extracts}"

        scored = []
        for doc in documents:
            doc_terms = _tokenize(doc)
            score = len(query_terms.intersection(doc_terms))
            scored.append((score, doc))

        scored.sort(reverse=True)
        top = [d for s, d in scored if s > 0][:3]

        if not top:
            extracts = "\n\n".join(documents[:2])
            return (
                "I don't have enough information to confidently answer from the documents.\n\n"
                f"Here are the most recent excerpts retrieved:\n\n{extracts}"
            )

        extracts = "\n\n".join(top)
        return (f"Answer generation is not available because no language model is configured. Here are most relevant"
                f"extracts from the documents:\n\n{extracts}")

