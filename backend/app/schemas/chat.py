import datetime
import uuid

from pydantic import BaseModel, Field


class ChatSessionCreate(BaseModel):
    title: str | None = None
    case_id: uuid.UUID | None = None


class ChatSessionResponse(BaseModel):
    id: uuid.UUID
    title: str | None
    status: str
    case_id: uuid.UUID | None = None
    follow_up_count: int = 0
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class ChatMessageSend(BaseModel):
    content: str
    attachment_text: str | None = None


class ChatMessageResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    role: str
    content: str
    tokens_used: int | None
    is_follow_up: bool = False
    attachments: dict | None = None
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class LinkCaseRequest(BaseModel):
    case_id: uuid.UUID


class FollowUpResult(BaseModel):
    needs_follow_up: bool
    question: str | None = None
    missing_info: list[str] = Field(default_factory=list)
