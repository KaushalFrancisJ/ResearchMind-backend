import hashlib
import json
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

UPLOADS_DIR = Path(__file__).resolve().parents[3] / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

from app.core.config import settings
from app.db.session import get_db
from app.repositories import chat_repo, chunk_repo, document_repo
from app.schemas.chat import QueryRequest, QueryResponse, RetrievedChunk, SessionCreate, SessionResponse
from app.services.chunking import extract_chunks_from_pdf
from app.services.retrieval.vector_search import vector_search

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


@router.post("/{session_id}/query", response_model=QueryResponse)
async def query_session(session_id: uuid.UUID, body: QueryRequest, db: AsyncSession = Depends(get_db)):
    chunks = await vector_search(db, session_id, body.query, body.top_k or settings.RETRIEVAL_TOP_K)
    return QueryResponse(
        query=body.query,
        chunks=[RetrievedChunk(**c) for c in chunks],
    )



async def create_session(body: SessionCreate, db: AsyncSession = Depends(get_db)):
    session = await chat_repo.create_session(db, body.session_title)
    return SessionResponse(
        session_id=session.session_id,
        session_title=session.session_title,
        last_active=session.updated_date,
    )
