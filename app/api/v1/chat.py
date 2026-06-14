from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories import chat_repo
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


@router.post("", response_model=SessionResponse, status_code=201)
async def create_session(body: SessionCreate, db: AsyncSession = Depends(get_db)):
    session = await chat_repo.create_session(db, body.session_title)
    return SessionResponse(
        session_id=session.session_id,
        session_title=session.session_title,
        last_active=session.updated_date,
    )
