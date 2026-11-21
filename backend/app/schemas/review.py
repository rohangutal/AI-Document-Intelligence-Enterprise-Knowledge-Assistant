"""Risk, obligation, and document-permission API schemas."""

from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class RiskReviewRequest(BaseModel):
    status: Literal["pending_review", "under_review", "accepted", "resolved"]
    note: str | None = Field(default=None, max_length=2000)


class RiskResponse(BaseModel):
    id: UUID
    contract_id: UUID
    clause_id: UUID | None
    title: str
    category: str
    severity: str
    explanation: str
    business_impact: str | None
    suggested_action: str | None
    review_status: str
    updated_at: datetime

    model_config = {"from_attributes": True}


class ObligationUpdate(BaseModel):
    status: Literal["open", "in_progress", "completed", "waived"] | None = None
    priority: Literal["low", "medium", "high", "critical"] | None = None
    due_date: date | None = None


class ObligationResponse(BaseModel):
    id: UUID
    contract_id: UUID
    clause_id: UUID | None
    responsible_party: str | None
    description: str
    due_date: date | None
    due_date_text: str | None
    priority: str
    status: str
    updated_at: datetime

    model_config = {"from_attributes": True}


class PermissionUpsertRequest(BaseModel):
    permission: Literal["read", "write", "admin"]


class PermissionResponse(BaseModel):
    document_id: UUID
    user_id: UUID
    permission: str

    model_config = {"from_attributes": True}
