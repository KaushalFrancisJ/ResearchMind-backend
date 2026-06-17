import hashlib
import json
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

UPLOADS_DIR = Path(__file__).resolve().parents[3] / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

from app.db.session import get_db
from app.repositories import chat_repo, document_repo
from app.schemas.chat import SessionCreate, SessionResponse
from app.services.chunking import extract_chunks_from_pdf

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

        await document_repo.link_to_session(db, session_id, doc.document_id)

        chunks = list(extract_chunks_from_pdf(str(dest)))

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

        results.append({"document_id": doc.document_id, "chunks_count": len(chunks)})

    return results


@router.post("", response_model=SessionResponse, status_code=201)
async def create_session(body: SessionCreate, db: AsyncSession = Depends(get_db)):
    session = await chat_repo.create_session(db, body.session_title)
    return SessionResponse(
        session_id=session.session_id,
        session_title=session.session_title,
        last_active=session.updated_date,
    )
