"""Add legal metadata used by structure-aware retrieval."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_legal_retrieval_metadata"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("contract_type", sa.String(80), nullable=True))
    op.add_column("documents", sa.Column("document_version", sa.String(80), nullable=True))
    op.add_column("document_chunks", sa.Column("section_number", sa.String(80), nullable=True))
    op.add_column("document_chunks", sa.Column("clause_category", sa.String(80), nullable=False, server_default="other"))
    op.add_column("document_chunks", sa.Column("contract_type", sa.String(80), nullable=True))
    op.add_column("document_chunks", sa.Column("document_version", sa.String(80), nullable=True))
    op.create_index("ix_document_chunks_clause_category", "document_chunks", ["clause_category"])
    op.create_index("ix_documents_contract_type", "documents", ["contract_type"])


def downgrade() -> None:
    op.drop_index("ix_documents_contract_type", table_name="documents")
    op.drop_index("ix_document_chunks_clause_category", table_name="document_chunks")
    op.drop_column("document_chunks", "document_version")
    op.drop_column("document_chunks", "contract_type")
    op.drop_column("document_chunks", "clause_category")
    op.drop_column("document_chunks", "section_number")
    op.drop_column("documents", "document_version")
    op.drop_column("documents", "contract_type")
