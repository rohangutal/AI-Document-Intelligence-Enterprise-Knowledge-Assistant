"""Core persistence entities for the enterprise knowledge platform."""

import uuid
from datetime import date, datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Department(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "departments"

    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    users: Mapped[list["User"]] = relationship(back_populates="department")
    documents: Mapped[list["Document"]] = relationship(back_populates="department")


class Role(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    users: Mapped[list["User"]] = relationship(back_populates="role")


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (Index("ix_users_email", "email"),)

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    department_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("departments.id"))
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id"), nullable=False)
    department: Mapped[Department | None] = relationship(back_populates="users")
    role: Mapped[Role] = relationship(back_populates="users")


class Document(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "documents"
    __table_args__ = (
        UniqueConstraint("content_hash", name="uq_documents_content_hash"),
        Index("ix_documents_status", "processing_status"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(120), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    processing_status: Mapped[str] = mapped_column(String(40), default="queued", nullable=False)
    contract_type: Mapped[str | None] = mapped_column(String(80))
    document_version: Mapped[str | None] = mapped_column(String(80))
    uploaded_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    department_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("departments.id"))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    uploaded_by: Mapped[User] = relationship()
    department: Mapped[Department | None] = relationship(back_populates="documents")
    chunks: Mapped[list["DocumentChunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    permissions: Mapped[list["DocumentPermission"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "document_chunks"
    __table_args__ = (Index("ix_document_chunks_document_index", "document_id", "chunk_index"),)

    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer)
    section_title: Mapped[str | None] = mapped_column(String(255))
    section_number: Mapped[str | None] = mapped_column(String(80))
    clause_category: Mapped[str] = mapped_column(String(80), default="other", nullable=False)
    contract_type: Mapped[str | None] = mapped_column(String(80))
    document_version: Mapped[str | None] = mapped_column(String(80))
    embedding: Mapped[list[float] | None] = mapped_column(Vector(768))
    document: Mapped[Document] = relationship(back_populates="chunks")


class Contract(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "contracts"
    __table_args__ = (Index("ix_contracts_type", "contract_type"), Index("ix_contracts_status", "status"))

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    contract_type: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="active", nullable=False)
    effective_date: Mapped[date | None] = mapped_column(Date)
    expiration_date: Mapped[date | None] = mapped_column(Date)
    document_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("documents.id", ondelete="SET NULL"))
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    document: Mapped[Document | None] = relationship()
    parties: Mapped[list["ContractParty"]] = relationship(back_populates="contract", cascade="all, delete-orphan")
    clauses: Mapped[list["ExtractedClause"]] = relationship(back_populates="contract", cascade="all, delete-orphan")
    risks: Mapped[list["ContractRisk"]] = relationship(back_populates="contract", cascade="all, delete-orphan")
    obligations: Mapped[list["ContractObligation"]] = relationship(back_populates="contract", cascade="all, delete-orphan")
    versions: Mapped[list["ContractVersion"]] = relationship(back_populates="contract", cascade="all, delete-orphan")


class ContractParty(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "contract_parties"

    contract_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str | None] = mapped_column(String(80))
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    contract: Mapped[Contract] = relationship(back_populates="parties")


class ExtractedClause(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "extracted_clauses"
    __table_args__ = (Index("ix_extracted_clauses_contract_category", "contract_id", "category"),)

    contract_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    document_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("documents.id", ondelete="SET NULL"))
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str | None] = mapped_column(String(255))
    text: Mapped[str] = mapped_column(Text, nullable=False)
    section_number: Mapped[str | None] = mapped_column(String(80))
    page_number: Mapped[int | None] = mapped_column(Integer)
    risk_level: Mapped[str] = mapped_column(String(30), default="low", nullable=False)
    contract: Mapped[Contract] = relationship(back_populates="clauses")


class ContractRisk(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "contract_risks"
    __table_args__ = (Index("ix_contract_risks_review_status", "review_status"),)

    contract_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    clause_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("extracted_clauses.id", ondelete="SET NULL"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    severity: Mapped[str] = mapped_column(String(30), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    business_impact: Mapped[str | None] = mapped_column(Text)
    suggested_action: Mapped[str | None] = mapped_column(Text)
    review_status: Mapped[str] = mapped_column(String(30), default="pending_review", nullable=False)
    contract: Mapped[Contract] = relationship(back_populates="risks")


class ContractObligation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "contract_obligations"
    __table_args__ = (Index("ix_contract_obligations_status", "status"),)

    contract_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    clause_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("extracted_clauses.id", ondelete="SET NULL"))
    responsible_party: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date)
    due_date_text: Mapped[str | None] = mapped_column(String(255))
    priority: Mapped[str] = mapped_column(String(30), default="medium", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="open", nullable=False)
    contract: Mapped[Contract] = relationship(back_populates="obligations")


class ContractVersion(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "contract_versions"
    __table_args__ = (UniqueConstraint("contract_id", "version_label", name="uq_contract_versions_label"),)

    contract_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    document_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("documents.id", ondelete="SET NULL"))
    version_label: Mapped[str] = mapped_column(String(80), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    contract: Mapped[Contract] = relationship(back_populates="versions")


class ClauseComparison(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "clause_comparisons"

    contract_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    original_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contract_versions.id", ondelete="CASCADE"), nullable=False)
    revised_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contract_versions.id", ondelete="CASCADE"), nullable=False)
    clause_type: Mapped[str] = mapped_column(String(80), nullable=False)
    change_type: Mapped[str] = mapped_column(String(30), nullable=False)
    original_text: Mapped[str | None] = mapped_column(Text)
    revised_text: Mapped[str | None] = mapped_column(Text)


class MissingClauseCheck(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "missing_clause_checks"
    __table_args__ = (UniqueConstraint("contract_id", "clause_type", name="uq_missing_clause_contract_type"),)

    contract_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    clause_type: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    requires_review: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class RiskReviewHistory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "risk_review_history"

    risk_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contract_risks.id", ondelete="CASCADE"), nullable=False)
    reviewer_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    from_status: Mapped[str | None] = mapped_column(String(30))
    to_status: Mapped[str] = mapped_column(String(30), nullable=False)
    note: Mapped[str | None] = mapped_column(Text)


class DocumentPermission(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "document_permissions"
    __table_args__ = (UniqueConstraint("document_id", "user_id", name="uq_document_permissions_user"),)

    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    permission: Mapped[str] = mapped_column(String(30), default="read", nullable=False)
    document: Mapped[Document] = relationship(back_populates="permissions")
    user: Mapped[User] = relationship()


class ProcessingJob(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "processing_jobs"

    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="queued", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Conversation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "conversations"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str | None] = mapped_column(String(255))
    user: Mapped[User] = relationship()
    messages: Mapped[list["Message"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")


class Message(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    conversation: Mapped[Conversation] = relationship(back_populates="messages")


class QueryLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "query_logs"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    retrieval_latency_ms: Mapped[int | None] = mapped_column(Integer)
    response_latency_ms: Mapped[int | None] = mapped_column(Integer)
    result_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class AuditLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "audit_logs"

    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    resource_type: Mapped[str | None] = mapped_column(String(80))
    resource_id: Mapped[uuid.UUID | None]
    details: Mapped[str | None] = mapped_column(Text)
