import hashlib
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

UPLOADS_DIR = Path(__file__).resolve().parents[3] / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

from app.db.session import get_db
from app.repositories import chat_repo, document_repo
from app.schemas.chat import SessionCreate, SessionResponse

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
async def upload_document(session_id: uuid.UUID, file: UploadFile, db: AsyncSession = Depends(get_db)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    contents = await file.read()
    file_hash = hashlib.sha256(contents).hexdigest()

    doc = await document_repo.get_by_hash(db, file_hash)
    if doc is None:
        dest = UPLOADS_DIR / f"{file_hash}.pdf"
        dest.write_bytes(contents)
        doc = await document_repo.create_document(db, str(dest), file_hash, file.filename)

    await document_repo.link_to_session(db, session_id, doc.document_id)
    return {"document_id": doc.document_id}


@router.post("", response_model=SessionResponse, status_code=201)
async def create_session(body: SessionCreate, db: AsyncSession = Depends(get_db)):
    session = await chat_repo.create_session(db, body.session_title)
    return SessionResponse(
        session_id=session.session_id,
        session_title=session.session_title,
        last_active=session.updated_date,
    )
