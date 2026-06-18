import uuid
from datetime import datetime

from pydantic import BaseModel


class SessionCreate(BaseModel):
    session_title: str


class SessionResponse(BaseModel):
    session_id: uuid.UUID
    session_title: str | None
    last_active: datetime

    model_config = {"from_attributes": True}


class QueryRequest(BaseModel):
    query: str
    top_k: int | None = None


class RetrievedChunk(BaseModel):
    chunk_id: int
    document_id: uuid.UUID
    chunk_index: int | None
    title: str | None
    content: str
    score: float


class QueryResponse(BaseModel):
    query: str
    chunks: list[RetrievedChunk]
