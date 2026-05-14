from __future__ import annotations

import datetime
import uuid
from pydantic import BaseModel, Field


class PersonInfo(BaseModel):
    name: str = ""
    id_number: str = ""
    contact: str = ""


class CaseCreate(BaseModel):
    title: str = Field(..., max_length=200)
    case_type: str
    plaintiff: PersonInfo = PersonInfo()
    defendant: PersonInfo = PersonInfo()
    claim_amount: float | None = None
    dispute_focus: list[str] | None = None
    assistant_id: uuid.UUID | None = None


class CaseUpdate(BaseModel):
    title: str | None = None
    case_type: str | None = None
    plaintiff: PersonInfo | None = None
    defendant: PersonInfo | None = None
    claim_amount: float | None = None
    dispute_focus: list[str] | None = None
    assistant_id: uuid.UUID | None = None


class CaseStatusUpdate(BaseModel):
    status: str


class CaseResponse(BaseModel):
    id: uuid.UUID
    case_number: str
    title: str
    case_type: str
    status: str
    plaintiff: dict
    defendant: dict
    claim_amount: float | None
    dispute_focus: list[str] | None
    lawyer_id: uuid.UUID
    assistant_id: uuid.UUID | None
    tenant_id: uuid.UUID
    gantt_data: dict | None
    ai_analysis: dict | None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


class CaseListResponse(BaseModel):
    items: list[CaseResponse]
    total: int
    page: int
    page_size: int


class EvidenceCreate(BaseModel):
    title: str = Field(..., max_length=200)
    evidence_type: str
    description: str | None = None
    sort_order: int = 0


class EvidenceUpdate(BaseModel):
    title: str | None = None
    evidence_type: str | None = None
    description: str | None = None
    sort_order: int | None = None


class EvidenceResponse(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    tenant_id: uuid.UUID
    title: str
    evidence_type: str
    file_url: str | None
    file_size: int | None
    file_type: str | None
    description: str | None
    sort_order: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


class TimelineCreate(BaseModel):
    event_type: str
    title: str = Field(..., max_length=200)
    description: str | None = None
    event_date: datetime.date


class TimelineUpdate(BaseModel):
    event_type: str | None = None
    title: str | None = None
    description: str | None = None
    event_date: datetime.date | None = None


class TimelineResponse(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    event_type: str
    title: str
    description: str | None
    event_date: datetime.date
    created_by: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}
