from fastapi import APIRouter, HTTPException
from app.schemas.rag import RAGQuery, RAGResponse
from app.services.rag_service import RAGService
from app.utils.vector_store import collection

router = APIRouter(
    prefix="/rag",
    tags=["RAG"]
)

rag_service = RAGService(collection)


@router.post(
    "/query",
    response_model=RAGResponse,
    summary="Role-based RAG query",
    description="Retrieves and answers using only documents authorized for the selected role."
)
def query_rag(payload: RAGQuery):
    try:
        answer, sources = rag_service.answer(
            role=payload.role,
            query=payload.query
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return RAGResponse(
        answer=answer,
        sources=sources
    )
