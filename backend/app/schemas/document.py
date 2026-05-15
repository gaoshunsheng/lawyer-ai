from __future__ import annotations

import datetime
import uuid
from pydantic import BaseModel, Field


class TemplateResponse(BaseModel):
    id: uuid.UUID
    name: str
    doc_type: str
    content_template: str
    variables_schema: dict
    category: str
    sort_order: int
    is_system: bool
    tenant_id: uuid.UUID | None
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class DocumentCreate(BaseModel):
    title: str = Field(..., max_length=200)
    doc_type: str
    template_id: uuid.UUID | None = None
    case_id: uuid.UUID | None = None
    variables: dict | None = None


class DocumentUpdate(BaseModel):
    title: str | None = None
    content: dict | None = None
    variables: dict | None = None
    status: str | None = None


class DocumentGenerateRequest(BaseModel):
    instructions: str | None = None


class DocumentResponse(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID | None
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    title: str
    doc_type: str
    template_id: uuid.UUID | None
    content: dict | None
    variables: dict | None
    status: str
    version: int
    parent_id: uuid.UUID | None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int
    page: int
    page_size: int
