"""Create the initial enterprise knowledge schema."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    uuid = postgresql.UUID(as_uuid=True)
    now = sa.DateTime(timezone=True)

    op.create_table("departments", sa.Column("id", uuid, primary_key=True), sa.Column("name", sa.String(120), nullable=False, unique=True), sa.Column("description", sa.Text()), sa.Column("created_at", now, nullable=False), sa.Column("updated_at", now, nullable=False))
    op.create_table("roles", sa.Column("id", uuid, primary_key=True), sa.Column("name", sa.String(80), nullable=False, unique=True), sa.Column("description", sa.Text()), sa.Column("created_at", now, nullable=False), sa.Column("updated_at", now, nullable=False))
    op.create_table("users", sa.Column("id", uuid, primary_key=True), sa.Column("email", sa.String(255), nullable=False, unique=True), sa.Column("full_name", sa.String(160), nullable=False), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False), sa.Column("department_id", uuid, sa.ForeignKey("departments.id")), sa.Column("role_id", uuid, sa.ForeignKey("roles.id"), nullable=False), sa.Column("created_at", now, nullable=False), sa.Column("updated_at", now, nullable=False))
    op.create_index("ix_users_email", "users", ["email"])
    op.create_table("documents", sa.Column("id", uuid, primary_key=True), sa.Column("name", sa.String(255), nullable=False), sa.Column("mime_type", sa.String(120), nullable=False), sa.Column("storage_key", sa.String(512), nullable=False), sa.Column("content_hash", sa.String(64), nullable=False, unique=True), sa.Column("processing_status", sa.String(40), nullable=False), sa.Column("uploaded_by_id", uuid, sa.ForeignKey("users.id"), nullable=False), sa.Column("department_id", uuid, sa.ForeignKey("departments.id")), sa.Column("uploaded_at", now, nullable=False), sa.Column("created_at", now, nullable=False), sa.Column("updated_at", now, nullable=False))
    op.create_index("ix_documents_status", "documents", ["processing_status"])
    op.create_table("document_chunks", sa.Column("id", uuid, primary_key=True), sa.Column("document_id", uuid, sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False), sa.Column("content", sa.Text(), nullable=False), sa.Column("chunk_index", sa.Integer(), nullable=False), sa.Column("page_number", sa.Integer()), sa.Column("section_title", sa.String(255)), sa.Column("embedding", Vector(768)), sa.Column("created_at", now, nullable=False), sa.Column("updated_at", now, nullable=False))
    op.create_index("ix_document_chunks_document_index", "document_chunks", ["document_id", "chunk_index"])
    op.create_table("document_permissions", sa.Column("id", uuid, primary_key=True), sa.Column("document_id", uuid, sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False), sa.Column("user_id", uuid, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("permission", sa.String(30), nullable=False), sa.Column("created_at", now, nullable=False), sa.Column("updated_at", now, nullable=False), sa.UniqueConstraint("document_id", "user_id", name="uq_document_permissions_user"))
    op.create_table("processing_jobs", sa.Column("id", uuid, primary_key=True), sa.Column("document_id", uuid, sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False), sa.Column("status", sa.String(40), nullable=False), sa.Column("error_message", sa.Text()), sa.Column("started_at", now), sa.Column("completed_at", now), sa.Column("created_at", now, nullable=False), sa.Column("updated_at", now, nullable=False))
    op.create_table("conversations", sa.Column("id", uuid, primary_key=True), sa.Column("user_id", uuid, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("title", sa.String(255)), sa.Column("created_at", now, nullable=False), sa.Column("updated_at", now, nullable=False))
    op.create_table("messages", sa.Column("id", uuid, primary_key=True), sa.Column("conversation_id", uuid, sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False), sa.Column("role", sa.String(30), nullable=False), sa.Column("content", sa.Text(), nullable=False), sa.Column("created_at", now, nullable=False), sa.Column("updated_at", now, nullable=False))
    op.create_table("query_logs", sa.Column("id", uuid, primary_key=True), sa.Column("user_id", uuid, sa.ForeignKey("users.id"), nullable=False), sa.Column("query", sa.Text(), nullable=False), sa.Column("retrieval_latency_ms", sa.Integer()), sa.Column("response_latency_ms", sa.Integer()), sa.Column("result_count", sa.Integer(), nullable=False), sa.Column("created_at", now, nullable=False), sa.Column("updated_at", now, nullable=False))
    op.create_table("audit_logs", sa.Column("id", uuid, primary_key=True), sa.Column("user_id", uuid, sa.ForeignKey("users.id")), sa.Column("action", sa.String(120), nullable=False), sa.Column("resource_type", sa.String(80)), sa.Column("resource_id", uuid), sa.Column("details", sa.Text()), sa.Column("created_at", now, nullable=False), sa.Column("updated_at", now, nullable=False))


def downgrade() -> None:
    for table in ("audit_logs", "query_logs", "messages", "conversations", "processing_jobs", "document_permissions", "document_chunks", "documents", "users", "roles", "departments"):
        op.drop_table(table)
