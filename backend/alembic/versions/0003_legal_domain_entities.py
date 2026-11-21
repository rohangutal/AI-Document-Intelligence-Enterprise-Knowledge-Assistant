"""Add persisted legal-domain entities for analysis and review workflows."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0003_legal_domain_entities"
down_revision: Union[str, None] = "0002_legal_retrieval_metadata"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    now = sa.DateTime(timezone=True)
    op.create_table("contracts", sa.Column("id", uuid, primary_key=True), sa.Column("name", sa.String(255), nullable=False), sa.Column("contract_type", sa.String(80), nullable=False), sa.Column("status", sa.String(40), nullable=False), sa.Column("effective_date", sa.Date()), sa.Column("expiration_date", sa.Date()), sa.Column("document_id", uuid, sa.ForeignKey("documents.id", ondelete="SET NULL")), sa.Column("created_by_id", uuid, sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("created_at", now, nullable=False), sa.Column("updated_at", now, nullable=False))
    op.create_index("ix_contracts_type", "contracts", ["contract_type"])
    op.create_index("ix_contracts_status", "contracts", ["status"])
    op.create_table("contract_parties", sa.Column("id", uuid, primary_key=True), sa.Column("contract_id", uuid, sa.ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False), sa.Column("name", sa.String(255), nullable=False), sa.Column("role", sa.String(80)), sa.Column("is_internal", sa.Boolean(), nullable=False), sa.Column("created_at", now, nullable=False), sa.Column("updated_at", now, nullable=False))
    op.create_table("extracted_clauses", sa.Column("id", uuid, primary_key=True), sa.Column("contract_id", uuid, sa.ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False), sa.Column("document_id", uuid, sa.ForeignKey("documents.id", ondelete="SET NULL")), sa.Column("category", sa.String(80), nullable=False), sa.Column("title", sa.String(255)), sa.Column("text", sa.Text(), nullable=False), sa.Column("section_number", sa.String(80)), sa.Column("page_number", sa.Integer()), sa.Column("risk_level", sa.String(30), nullable=False), sa.Column("created_at", now, nullable=False), sa.Column("updated_at", now, nullable=False))
    op.create_index("ix_extracted_clauses_contract_category", "extracted_clauses", ["contract_id", "category"])
    op.create_table("contract_risks", sa.Column("id", uuid, primary_key=True), sa.Column("contract_id", uuid, sa.ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False), sa.Column("clause_id", uuid, sa.ForeignKey("extracted_clauses.id", ondelete="SET NULL")), sa.Column("title", sa.String(255), nullable=False), sa.Column("category", sa.String(80), nullable=False), sa.Column("severity", sa.String(30), nullable=False), sa.Column("explanation", sa.Text(), nullable=False), sa.Column("business_impact", sa.Text()), sa.Column("suggested_action", sa.Text()), sa.Column("review_status", sa.String(30), nullable=False), sa.Column("created_at", now, nullable=False), sa.Column("updated_at", now, nullable=False))
    op.create_index("ix_contract_risks_review_status", "contract_risks", ["review_status"])
    op.create_table("contract_obligations", sa.Column("id", uuid, primary_key=True), sa.Column("contract_id", uuid, sa.ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False), sa.Column("clause_id", uuid, sa.ForeignKey("extracted_clauses.id", ondelete="SET NULL")), sa.Column("responsible_party", sa.String(255)), sa.Column("description", sa.Text(), nullable=False), sa.Column("due_date", sa.Date()), sa.Column("due_date_text", sa.String(255)), sa.Column("priority", sa.String(30), nullable=False), sa.Column("status", sa.String(30), nullable=False), sa.Column("created_at", now, nullable=False), sa.Column("updated_at", now, nullable=False))
    op.create_index("ix_contract_obligations_status", "contract_obligations", ["status"])
    op.create_table("contract_versions", sa.Column("id", uuid, primary_key=True), sa.Column("contract_id", uuid, sa.ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False), sa.Column("document_id", uuid, sa.ForeignKey("documents.id", ondelete="SET NULL")), sa.Column("version_label", sa.String(80), nullable=False), sa.Column("version_number", sa.Integer(), nullable=False), sa.Column("is_current", sa.Boolean(), nullable=False), sa.Column("created_at", now, nullable=False), sa.Column("updated_at", now, nullable=False), sa.UniqueConstraint("contract_id", "version_label", name="uq_contract_versions_label"))
    op.create_table("clause_comparisons", sa.Column("id", uuid, primary_key=True), sa.Column("contract_id", uuid, sa.ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False), sa.Column("original_version_id", uuid, sa.ForeignKey("contract_versions.id", ondelete="CASCADE"), nullable=False), sa.Column("revised_version_id", uuid, sa.ForeignKey("contract_versions.id", ondelete="CASCADE"), nullable=False), sa.Column("clause_type", sa.String(80), nullable=False), sa.Column("change_type", sa.String(30), nullable=False), sa.Column("original_text", sa.Text()), sa.Column("revised_text", sa.Text()), sa.Column("created_at", now, nullable=False), sa.Column("updated_at", now, nullable=False))
    op.create_table("missing_clause_checks", sa.Column("id", uuid, primary_key=True), sa.Column("contract_id", uuid, sa.ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False), sa.Column("clause_type", sa.String(80), nullable=False), sa.Column("status", sa.String(30), nullable=False), sa.Column("requires_review", sa.Boolean(), nullable=False), sa.Column("created_at", now, nullable=False), sa.Column("updated_at", now, nullable=False), sa.UniqueConstraint("contract_id", "clause_type", name="uq_missing_clause_contract_type"))
    op.create_table("risk_review_history", sa.Column("id", uuid, primary_key=True), sa.Column("risk_id", uuid, sa.ForeignKey("contract_risks.id", ondelete="CASCADE"), nullable=False), sa.Column("reviewer_id", uuid, sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("from_status", sa.String(30)), sa.Column("to_status", sa.String(30), nullable=False), sa.Column("note", sa.Text()), sa.Column("created_at", now, nullable=False), sa.Column("updated_at", now, nullable=False))


def downgrade() -> None:
    for table in ("risk_review_history", "missing_clause_checks", "clause_comparisons", "contract_versions", "contract_obligations", "contract_risks", "extracted_clauses", "contract_parties", "contracts"):
        op.drop_table(table)
