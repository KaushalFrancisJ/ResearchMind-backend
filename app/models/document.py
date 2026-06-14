import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Session(Base):
    __tablename__ = "sessions"

    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    session_title: Mapped[str | None] = mapped_column(String, nullable=True)
    created_date: Mapped[datetime] = mapped_column(nullable=False, server_default=func.current_timestamp())
    updated_date: Mapped[datetime] = mapped_column(nullable=False, server_default=func.current_timestamp())

    session_documents: Mapped[list["SessionDocument"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    document_path: Mapped[str] = mapped_column(String, nullable=False)
    document_hash: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    document_title: Mapped[str | None] = mapped_column(String, nullable=True)
    created_date: Mapped[datetime] = mapped_column(nullable=False, server_default=func.current_timestamp())

    session_documents: Mapped[list["SessionDocument"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class SessionDocument(Base):
    __tablename__ = "session_documents"
    __table_args__ = (UniqueConstraint("session_id", "document_id", name="uq_session_documents"),)

    session_document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=False)

    session: Mapped["Session"] = relationship(back_populates="session_documents")
    document: Mapped["Document"] = relationship(back_populates="session_documents")
