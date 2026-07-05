import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMode, ChatRole, SessionChat
from app.models.document import Session


async def get_sessions(db: AsyncSession) -> list[Session]:
    result = await db.execute(select(Session).order_by(Session.updated_date.desc()))
    return list(result.scalars().all())


async def create_session(db: AsyncSession, title: str) -> Session:
    session = Session(session_title=title)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_chat_history(
    db: AsyncSession,
    session_id: uuid.UUID,
    page: int,
    page_size: int,
) -> tuple[int, list[SessionChat]]:
    """Return (total_count, records) ordered latest → oldest with offset pagination."""
    base_filter = SessionChat.session_id == session_id

    total: int = (
        await db.execute(select(func.count()).where(base_filter))
    ).scalar_one()

    result = await db.execute(
        select(SessionChat)
        .where(base_filter)
        .order_by(SessionChat.created_date.desc(), SessionChat.session_chat_id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    records = list(result.scalars().all())
    return total, records


async def save_chat(
    db: AsyncSession,
    session_id: uuid.UUID,
    query: str,
    answer: str,
    mode: str,
    model_used: str,
    retrieved_chunks: list[dict] | None = None,
    parent_chat_id: int | None = None,
) -> SessionChat:
    """Persist a query/answer pair to the session_chat table.

    Stores both the user turn and the assistant turn as a single row
    (query + answer on the same record) for simplicity, using the
    assistant role to mark it as an AI response.
    """
    chat_mode = ChatMode.thinking if mode == "thinking" else ChatMode.fast

    record = SessionChat(
        session_id=session_id,
        parent_chat_id=parent_chat_id,
        role=ChatRole.assistant,
        mode=chat_mode,
        model_used=model_used,
        query=query,
        answer=answer,
        retrieved_chunks=retrieved_chunks,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record
