from fastapi import APIRouter, HTTPException
from app.schemas.rag import RAGQuery, RAGResponse
from app.services.rag_service import RAGService
from app.utils.vector_store import collection
from app.utils.llm import LLMClient

router = APIRouter(
    prefix="/rag",
    tags=["RAG"]
)
llm = LLMClient(model="gemini-2.5-flash")

rag_service = RAGService(collection, llm)


@router.post(
    "/query",
    response_model=RAGResponse,
    summary="Role-based RAG query",
    description="Retrieves and answers using only documents authorized for the selected role."
)
def query_rag(payload: RAGQuery):
    try:
        answer, sources, context_chunks = rag_service.answer(
            role=payload.role,
            query=payload.query,
        )
        final_answer = rag_service.generate_answer(
            documents=context_chunks,
            query=payload.query,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return RAGResponse(
        answer=final_answer,
        sources=sources
    )

@router.post(
    "/fetch_docs",
    response_model=RAGResponse,
    summary="Role-based RAG query docs",
    description="Retrieves the documents for a given query and role without generating an answer."
)
def fetch_docs(payload: RAGQuery):
    try:
        answer, sources, context_chunks = rag_service.answer(
            role=payload.role,
            query=payload.query,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return RAGResponse(
        answer=answer,
        sources=sources
    )

