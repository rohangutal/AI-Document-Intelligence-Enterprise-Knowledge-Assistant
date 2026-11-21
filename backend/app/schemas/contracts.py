"""Contract resource schemas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ContractCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    contract_type: str = Field(min_length=1, max_length=80)
    status: str = Field(default="active", max_length=40)
    effective_date: date | None = None
    expiration_date: date | None = None
    document_id: UUID | None = None


class ContractResponse(BaseModel):
    id: UUID
    name: str
    contract_type: str
    status: str
    effective_date: date | None
    expiration_date: date | None
    document_id: UUID | None
    created_by_id: UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ContractListResponse(BaseModel):
    items: list[ContractResponse]
    total: int
    limit: int
    offset: int


class ContractAnalysisResponse(BaseModel):
    contract_id: UUID
    status: str
    clause_count: int
    risk_count: int
    obligation_count: int
