from recycle.app.services.rag_service import RAGService
from recycle.app.utils.vector_store import vector_store

rag_service = RAGService(vector_store)

def handle_rag_query(role: str, query: str):
    """
    Handle a RAG query for a specific user role.
    :param role: Role of the user making the query
    :param query: The user's query
    :return: The answer from the RAG system
    """
    answer, sources = rag_service.answer(role, query)
    return answer, sources