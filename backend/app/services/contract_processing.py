"""Persisted analysis orchestration for uploaded contracts."""

from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.entities import Contract, ContractObligation, ContractRisk, DocumentChunk, ExtractedClause
from app.services.legal_analysis import extract_clauses


def analyze_persisted_contract(db: Session, contract: Contract) -> dict[str, int | str]:
    """Analyze source chunks and replace the contract's derived analysis records."""
    if contract.document_id is None:
        raise ValueError("Contract has no source document")
    chunks = list(db.scalars(select(DocumentChunk).where(DocumentChunk.document_id == contract.document_id).order_by(DocumentChunk.chunk_index)))
    if not chunks:
        raise ValueError("Contract source document has no extracted text chunks")

    db.execute(delete(ContractRisk).where(ContractRisk.contract_id == contract.id))
    db.execute(delete(ContractObligation).where(ContractObligation.contract_id == contract.id))
    db.execute(delete(ExtractedClause).where(ExtractedClause.contract_id == contract.id))

    clause_count = risk_count = obligation_count = 0
    for source_chunk in chunks:
        for result in extract_clauses(source_chunk.content):
            clause = ExtractedClause(
                contract_id=contract.id,
                document_id=contract.document_id,
                category=str(result["clause_type"]),
                title=result["title"],
                text=str(result["text"]),
                section_number=source_chunk.section_number,
                page_number=source_chunk.page_number,
                risk_level=str(result["risk_level"]),
            )
            db.add(clause)
            db.flush()
            clause_count += 1
            risk_reasons = [str(reason) for reason in result["risk_reasons"]]
            if str(result["risk_level"]) != "low":
                db.add(ContractRisk(
                    contract_id=contract.id,
                    clause_id=clause.id,
                    title=f"Potential {result['clause_type']} concern",
                    category=str(result["clause_type"]),
                    severity=str(result["risk_level"]),
                    explanation=" ".join(risk_reasons) or "This provision requires human review.",
                    business_impact="Potential contractual or operational exposure should be assessed.",
                    suggested_action="Review the original clause with qualified counsel.",
                ))
                risk_count += 1
            for obligation_text in result["obligations"]:
                db.add(ContractObligation(
                    contract_id=contract.id,
                    clause_id=clause.id,
                    description=str(obligation_text),
                    due_date_text="Date or timing requires review",
                    priority="medium",
                ))
                obligation_count += 1

    contract.status = "review"
    if contract.document is not None:
        contract.document.processing_status = "analyzed"
    db.commit()
    return {"status": "completed", "clause_count": clause_count, "risk_count": risk_count, "obligation_count": obligation_count}
