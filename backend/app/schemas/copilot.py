from pydantic import BaseModel
from typing import List

class QueryRequest(BaseModel):
    query: str

class Citation(BaseModel):
    document: str
    chunk: int
    score: float
    document_id: str

class QueryResponse(BaseModel):
    answer: str
    confidence: float
    citations: List[Citation]
    documents_used: List[str]
    processing_time: str
