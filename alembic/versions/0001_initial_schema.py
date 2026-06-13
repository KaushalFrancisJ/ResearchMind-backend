"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-06-10
"""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "sessions",
        sa.Column("session_id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("session_title", sa.String(), nullable=True),
        sa.Column("created_date", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_date", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "documents",
        sa.Column("document_id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("document_path", sa.String(), nullable=False),
        sa.Column("document_hash", sa.String(), nullable=False),
        sa.Column("document_title", sa.String(), nullable=True),
        sa.Column("created_date", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_documents_document_hash", "documents", ["document_hash"], unique=True)

    op.create_table(
        "session_documents",
        sa.Column("session_document_id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("session_id", sa.UUID(), sa.ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_id", sa.UUID(), sa.ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("session_id", "document_id", name="uq_session_documents"),
    )

    op.create_table(
        "document_chunks",
        sa.Column("chunk_id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("document_id", sa.UUID(), sa.ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("embedding", Vector(384), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("chunk_index", sa.Integer(), nullable=True),
        sa.Column("created_date", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_document_chunks_document_id", "document_chunks", ["document_id"])

    op.create_table(
        "session_chat",
        sa.Column("session_chat_id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.UUID(), sa.ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False),
        sa.Column("parent_chat_id", sa.BigInteger(), sa.ForeignKey("session_chat.session_chat_id", ondelete="SET NULL"), nullable=True),
        sa.Column("role", sa.Enum("user", "assistant", name="chat_role", create_type=True), nullable=False),
        sa.Column("mode", sa.Enum("fast", "thinking", name="chat_mode", create_type=True), nullable=True),
        sa.Column("model_used", sa.String(), nullable=True),
        sa.Column("query", sa.Text(), nullable=True),
        sa.Column("answer", sa.Text(), nullable=True),
        sa.Column("retrieved_chunks", sa.JSON(), nullable=True),
        sa.Column("created_date", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_session_chat_session_id", "session_chat", ["session_id"])

    op.create_table(
        "session_summary",
        sa.Column("summary_id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("session_id", sa.UUID(), sa.ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False),
        sa.Column("summary_text", sa.Text(), nullable=True),
        sa.Column("covers_upto_chat_id", sa.BigInteger(), sa.ForeignKey("session_chat.session_chat_id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_date", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "chat_evaluation",
        sa.Column("chat_evaluation_id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("session_chat_id", sa.BigInteger(), sa.ForeignKey("session_chat.session_chat_id", ondelete="CASCADE"), nullable=False),
        sa.Column("faithfulness_score", sa.Float(), nullable=True),
        sa.Column("faithfulness_reason", sa.Text(), nullable=True),
        sa.Column("relevancy_score", sa.Float(), nullable=True),
        sa.Column("relevancy_reason", sa.Text(), nullable=True),
        sa.Column("created_date", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )


def downgrade() -> None:
    op.drop_table("chat_evaluation")
    op.drop_table("session_summary")
    op.drop_index("ix_session_chat_session_id", "session_chat")
    op.drop_table("session_chat")
    op.drop_index("ix_document_chunks_document_id", "document_chunks")
    op.drop_table("document_chunks")
    op.drop_table("session_documents")
    op.drop_index("ix_documents_document_hash", "documents")
    op.drop_table("documents")
    op.drop_table("sessions")
    op.execute("DROP TYPE IF EXISTS chat_mode")
    op.execute("DROP TYPE IF EXISTS chat_role")
