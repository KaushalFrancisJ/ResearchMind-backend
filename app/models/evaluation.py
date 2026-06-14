import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Float, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ChatEvaluation(Base):
    __tablename__ = "chat_evaluation"

    chat_evaluation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    session_chat_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("session_chat.session_chat_id", ondelete="CASCADE"), nullable=False)
    faithfulness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    faithfulness_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    relevancy_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    relevancy_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_date: Mapped[datetime] = mapped_column(nullable=False, server_default=func.current_timestamp())
