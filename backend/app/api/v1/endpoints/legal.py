"""Legal-document analysis endpoints."""

from fastapi import APIRouter

from app.agents.legal_workflow import run_legal_workflow
from app.schemas.legal import (
    ClauseAnalysisRequest,
    ClauseAnalysisResponse,
    DocumentComparisonRequest,
    DocumentComparisonResponse,
    RetrievalRequest,
    RetrievalResponse,
    LegalWorkflowRequest,
    LegalWorkflowResponse,
    ContractSummaryRequest,
    ContractSummaryResponse,
    MissingClauseRequest,
    MissingClauseResponse,
)
from app.services.legal_analysis import compare_contracts, extract_clauses, missing_clause_checks, retrieve_chunks, summarize_contract

router = APIRouter(prefix="/legal", tags=["legal analysis"])


@router.post("/workflow", response_model=LegalWorkflowResponse)
def run_workflow(request: LegalWorkflowRequest) -> LegalWorkflowResponse:
    state = run_legal_workflow(
        task=request.task,
        question=request.question,
        document_text=request.document_text,
        chunks=[chunk.model_dump() for chunk in request.chunks],
        top_k=request.top_k,
    )
    return LegalWorkflowResponse(
        task=request.task,
        answer=state.get("answer", ""),
        evidence_valid=state.get("evidence_valid", False),
        citations=state.get("citations", []),
        clauses=state.get("clauses", []),
        risks=state.get("risks", []),
        obligations=state.get("obligations", []),
        warnings=state.get("warnings", []),
    )


@router.post("/clauses", response_model=ClauseAnalysisResponse)
def analyze_clauses(request: ClauseAnalysisRequest) -> ClauseAnalysisResponse:
    clauses = extract_clauses(request.text)
    return ClauseAnalysisResponse(
        clauses=clauses,
        risks_found=sum(item["risk_level"] != "low" for item in clauses),
        obligations_found=sum(len(item["obligations"]) for item in clauses),
    )


@router.post("/compare", response_model=DocumentComparisonResponse)
def compare(request: DocumentComparisonRequest) -> DocumentComparisonResponse:
    return DocumentComparisonResponse(**compare_contracts(request.original_text, request.revised_text))


@router.post("/missing-clauses", response_model=MissingClauseResponse)
def check_missing_clauses(request: MissingClauseRequest) -> MissingClauseResponse:
    return MissingClauseResponse(contract_type=request.contract_type, checks=missing_clause_checks(request.document_text, request.contract_type))


@router.post("/summary", response_model=ContractSummaryResponse)
def summarize(request: ContractSummaryRequest) -> ContractSummaryResponse:
    return ContractSummaryResponse(**summarize_contract(request.document_text, request.contract_type))


@router.post("/retrieve", response_model=RetrievalResponse)
def retrieve(request: RetrievalRequest) -> RetrievalResponse:
    return RetrievalResponse(
        results=retrieve_chunks(
            request.query,
            [chunk.model_dump() for chunk in request.chunks],
            request.top_k,
            similarity_threshold=request.similarity_threshold,
            metadata_filters=request.metadata_filters,
        )
    )
