"""Request and response contracts for legal document analysis."""

from typing import Literal

from pydantic import BaseModel, Field


class ClauseAnalysisRequest(BaseModel):
    text: str = Field(min_length=1, description="Plain text extracted from a legal document.")


class ClauseResult(BaseModel):
    clause_type: str
    title: str | None = None
    text: str
    source_start: int
    source_end: int
    risk_level: str
    risk_reasons: list[str] = Field(default_factory=list)
    obligations: list[str] = Field(default_factory=list)


class ClauseAnalysisResponse(BaseModel):
    clauses: list[ClauseResult]
    risks_found: int
    obligations_found: int


class DocumentComparisonRequest(BaseModel):
    original_text: str = Field(min_length=1)
    revised_text: str = Field(min_length=1)


class DocumentChange(BaseModel):
    change_type: str
    original: str | None = None
    revised: str | None = None


class DocumentComparisonResponse(BaseModel):
    changed: bool
    additions: int
    deletions: int
    changes: list[DocumentChange]
    clause_changes: list[dict[str, object]] = Field(default_factory=list)
    modified_clauses: int = 0


class MissingClauseRequest(BaseModel):
    contract_type: str = Field(min_length=1)
    document_text: str = Field(min_length=1)


class MissingClauseCheck(BaseModel):
    clause_type: str
    status: Literal["present", "missing"]
    requires_review: bool


class MissingClauseResponse(BaseModel):
    contract_type: str
    checks: list[MissingClauseCheck]


class ContractSummaryRequest(BaseModel):
    document_text: str = Field(min_length=1)
    contract_type: str | None = None


class ContractSummaryResponse(BaseModel):
    contract_type: str | None
    parties: list[str]
    dates: list[str]
    clause_count: int
    risk_count: int
    obligation_count: int
    key_clauses: list[dict[str, object]]
    review_notice: str


class RetrievalChunk(BaseModel):
    chunk_id: str
    content: str = Field(min_length=1)
    document_name: str | None = None
    page_number: int | None = None
    section_number: str | None = None
    section_title: str | None = None
    clause_category: str | None = None
    contract_type: str | None = None
    document_version: str | None = None
    embedding: list[float] | None = None


class RetrievalRequest(BaseModel):
    query: str = Field(min_length=1)
    chunks: list[RetrievalChunk] = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    similarity_threshold: float = Field(default=0.0, ge=0.0, le=1.0)
    metadata_filters: dict[str, str] | None = None


class RetrievedChunk(RetrievalChunk):
    score: float
    citation: str


class RetrievalResponse(BaseModel):
    results: list[RetrievedChunk]


class LegalWorkflowRequest(BaseModel):
    task: Literal["question", "risk", "obligation", "summary"]
    question: str = ""
    document_text: str = ""
    chunks: list[RetrievalChunk] = Field(default_factory=list)
    top_k: int = Field(default=5, ge=1, le=20)


class LegalWorkflowResponse(BaseModel):
    task: str
    answer: str
    evidence_valid: bool
    citations: list[str]
    clauses: list[dict[str, object]] = Field(default_factory=list)
    risks: list[dict[str, object]] = Field(default_factory=list)
    obligations: list[dict[str, object]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
