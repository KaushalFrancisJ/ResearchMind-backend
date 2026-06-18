import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, SessionDocument


async def get_by_hash(db: AsyncSession, file_hash: str) -> Document | None:
    result = await db.execute(select(Document).where(Document.document_hash == file_hash))
    return result.scalar_one_or_none()


async def create_document(db: AsyncSession, path: str, file_hash: str, title: str | None) -> Document:
    doc = Document(document_path=path, document_hash=file_hash, document_title=title)
    db.add(doc)
    await db.flush()
    return doc


async def link_to_session(db: AsyncSession, session_id: uuid.UUID, document_id: uuid.UUID) -> None:
    existing = await db.execute(
        select(SessionDocument).where(
            SessionDocument.session_id == session_id,
            SessionDocument.document_id == document_id,
        )
    )
    if existing.scalar_one_or_none() is None:
        db.add(SessionDocument(session_id=session_id, document_id=document_id))
