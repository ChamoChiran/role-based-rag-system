from recycle.app.utils.vector_store import collection

class RAGService:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def answer(self,role:str, query:str):
        """
        Role-based RAG using metadata boolean flags.
        :param role: Role of the user making the query
        :param query: The user's query
        :return: The answer from the RAG system
        """

        role_flag = f"role_{role}"

        # Retrieve relevant chunks WITH role filtering
        results = collection.query(
            query_texts=query,
            n_retrieve=5,
            where={role_flag: role}
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        if not results:
            return (
                "No accessible information found for your role regarding this query.",
                []
            )

        # Build context
        context_chunks = []
        sources = []

        for doc, meta in zip(documents, metadatas):
            context_chunks.append(doc)
            sources.append(meta.get("source", "Unknown"))

        context_text = "\n\n".join(context_chunks)

        return context_text, list(set(sources))