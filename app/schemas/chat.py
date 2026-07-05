import uuid
from datetime import datetime
from typing import Literal

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


# ── Chat (RAG + LLM) ─────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    query: str
    mode: Literal["fast", "thinking"] = "fast"
    top_k: int | None = None


class ChatResponse(BaseModel):
    session_chat_id: int
    query: str
    answer: str
    mode: str
    model_used: str
    chunks: list[RetrievedChunk]


# ── Chat history ──────────────────────────────────────────────────────────────

class ChatHistoryItem(BaseModel):
    session_chat_id: int
    query: str | None
    answer: str | None
    mode: str | None
    model_used: str | None
    created_date: datetime

    model_config = {"from_attributes": True}


class ChatHistoryResponse(BaseModel):
    session_id: uuid.UUID
    total: int
    page: int
    page_size: int
    items: list[ChatHistoryItem]
