from pydantic import BaseModel
from typing import List

class RAGQuery(BaseModel):
    role: str
    query: str

class RAGResponse(BaseModel):
    answer: str
    sources: List[str]