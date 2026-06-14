from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
