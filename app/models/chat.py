import enum
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Enum, ForeignKey, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ChatRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"


class ChatMode(str, enum.Enum):
    fast = "fast"
    thinking = "thinking"


class SessionChat(Base):
    __tablename__ = "session_chat"

    session_chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False, index=True)
    parent_chat_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("session_chat.session_chat_id", ondelete="SET NULL"), nullable=True)
    role: Mapped[ChatRole] = mapped_column(Enum(ChatRole, name="chat_role", create_type=False), nullable=False)
    mode: Mapped[ChatMode | None] = mapped_column(Enum(ChatMode, name="chat_mode", create_type=False), nullable=True)
    model_used: Mapped[str | None] = mapped_column(String, nullable=True)
    query: Mapped[str | None] = mapped_column(Text, nullable=True)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    retrieved_chunks: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_date: Mapped[datetime] = mapped_column(nullable=False, server_default=func.current_timestamp())


class SessionSummary(Base):
    __tablename__ = "session_summary"

    summary_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False)
    summary_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    covers_upto_chat_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("session_chat.session_chat_id", ondelete="SET NULL"), nullable=True)
    created_date: Mapped[datetime] = mapped_column(nullable=False, server_default=func.current_timestamp())
