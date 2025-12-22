from fastapi import APIRouter, HTTPException
from recycle.app.types.rag import RAGQuery, RAGResponse
from recycle.app.controllers.rag import handle_rag_query

router = APIRouter(tags=["RAG"])

@router.post(
    "/rag/query",
    response_model=RAGResponse,
    summary="RAG query for a specific user",
    description="Retrieves and answers using only chunks authorized for the selected role.",
)
def query_rag(payload: RAGQuery):
    try:
        answer, sources = handle_rag_query(
            role=payload.role,
            query=payload.query
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return RAGResponse(
        answer=answer,
        sources=sources
    )