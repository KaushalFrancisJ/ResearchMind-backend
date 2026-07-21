import hashlib
import json
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.repositories import chat_repo, chunk_repo, document_repo
from app.schemas.chat import (
    ChatHistoryItem,
    ChatHistoryResponse,
    ChatRequest,
    ChatResponse,
    QueryRequest,
    QueryResponse,
    RetrievedChunk,
    SessionCreate,
    SessionResponse,
)
from app.schemas.document import SessionDocumentItem
from app.services.chunking import extract_chunks_from_pdf
from app.services.llm import generate
from app.services.retrieval.vector_search import vector_search

# Get uploads directory from settings
UPLOADS_DIR = Path(settings.UPLOADS_DIR)
UPLOADS_DIR.mkdir(exist_ok=True)

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("", response_model=list[SessionResponse])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    sessions = await chat_repo.get_sessions(db)
    return [
        SessionResponse(
            session_id=s.session_id,
            session_title=s.session_title,
            last_active=s.updated_date,
        )
        for s in sessions
    ]


@router.post("", response_model=SessionResponse, status_code=201)
async def create_session(body: SessionCreate, db: AsyncSession = Depends(get_db)):
    session = await chat_repo.create_session(db, body.session_title)
    return SessionResponse(
        session_id=session.session_id,
        session_title=session.session_title,
        last_active=session.updated_date,
    )


@router.post("/{session_id}/upload", status_code=200)
async def upload_document(session_id: uuid.UUID, files: list[UploadFile], db: AsyncSession = Depends(get_db)):
    results = []
    for file in files:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail=f"{file.filename}: only PDF files are accepted")

        contents = await file.read()
        file_hash = hashlib.sha256(contents).hexdigest()

        dest = UPLOADS_DIR / f"{file_hash}.pdf"

        doc = await document_repo.get_by_hash(db, file_hash)
        if doc is None:
            dest.write_bytes(contents)
            doc = await document_repo.create_document(db, str(dest), file_hash, file.filename)

            chunks = list(extract_chunks_from_pdf(str(dest)))
            await chunk_repo.save_chunks(db, doc.document_id, chunks)

            chunks_file = UPLOADS_DIR / f"{file_hash}_chunks.json"
            chunks_file.write_text(
                json.dumps([{"id": c.id, "module": c.module, "title": c.title, "content": c.content} for c in chunks],
                           ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            content_file = UPLOADS_DIR / f"{file_hash}_content.txt"
            lines = []
            for c in chunks:
                lines.append(f"=== {c.title} ===")
                lines.append(c.content)
                lines.append("")
            content_file.write_text("\n".join(lines), encoding="utf-8")
        else:
            chunks = json.loads((UPLOADS_DIR / f"{file_hash}_chunks.json").read_text(encoding="utf-8"))

        await document_repo.link_to_session(db, session_id, doc.document_id)
        results.append({"document_id": doc.document_id, "chunks_count": len(chunks)})

    await db.commit()
    return results


@router.get("/{session_id}/documents", response_model=list[SessionDocumentItem])
async def list_session_documents(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """List all documents uploaded to a session, newest first."""
    docs = await document_repo.get_session_documents(db, session_id)
    return [SessionDocumentItem.model_validate(d) for d in docs]


@router.get("/{session_id}/chat", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: uuid.UUID,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve paginated chat history for a session, latest messages first.

    - **page**: 1-based page number (default: 1)
    - **page_size**: records per page, max 100 (default: 20)
    """
    if page < 1:
        raise HTTPException(status_code=400, detail="page must be >= 1")
    if not 1 <= page_size <= 100:
        raise HTTPException(status_code=400, detail="page_size must be between 1 and 100")

    total, records = await chat_repo.get_chat_history(db, session_id, page, page_size)

    return ChatHistoryResponse(
        session_id=session_id,
        total=total,
        page=page,
        page_size=page_size,
        items=[ChatHistoryItem.model_validate(r) for r in records],
    )


@router.post("/{session_id}/query", response_model=QueryResponse)
async def query_session(session_id: uuid.UUID, body: QueryRequest, db: AsyncSession = Depends(get_db)):
    """Pure retrieval endpoint — returns chunks without calling an LLM."""
    chunks = await vector_search(db, session_id, body.query, body.top_k or settings.RETRIEVAL_TOP_K)
    return QueryResponse(
        query=body.query,
        chunks=[RetrievedChunk(**c) for c in chunks],
    )


@router.post("/{session_id}/chat", response_model=ChatResponse)
async def chat_session(session_id: uuid.UUID, body: ChatRequest, db: AsyncSession = Depends(get_db)):
    """RAG + LLM endpoint.

    1. Retrieves relevant chunks for the query.
    2. Calls the configured LLM (Ollama in dev, Groq in production).
    3. Persists the query/answer pair to session_chat.
    """
    top_k = body.top_k or settings.RETRIEVAL_TOP_K
    chunks = await vector_search(db, session_id, body.query, top_k)

    if not chunks:
        raise HTTPException(status_code=404, detail="No relevant documents found for this session.")

    context = "\n\n".join(c["content"] for c in chunks)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful research assistant. "
                "Use only the provided context to answer the user's question. "
                "If the answer is not in the context, say so."
            ),
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {body.query}",
        },
    ]

    answer, model_used = generate(messages, mode=body.mode)

    retrieved_chunks_json = [
        {
            "chunk_id": c["chunk_id"],
            "document_id": str(c["document_id"]),
            "chunk_index": c.get("chunk_index"),
            "title": c.get("title"),
            "score": c["score"],
        }
        for c in chunks
    ]

    record = await chat_repo.save_chat(
        db=db,
        session_id=session_id,
        query=body.query,
        answer=answer,
        mode=body.mode,
        model_used=model_used,
        retrieved_chunks=retrieved_chunks_json,
    )

    return ChatResponse(
        session_chat_id=record.session_chat_id,
        query=body.query,
        answer=answer,
        mode=body.mode,
        model_used=model_used,
        chunks=[RetrievedChunk(**c) for c in chunks],
    )
