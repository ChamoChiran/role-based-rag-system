from pydantic import BaseModel
from typing import List

class RAGQuery(BaseModel):
    """
    Incoming user question.
    """
    role: str
    query: str

class RAGResponse(BaseModel):
    """
    Model returned to the client.
    """
    answer: str
    sources: List[str]