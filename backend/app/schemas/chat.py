import datetime
import uuid

from pydantic import BaseModel


class ChatSessionCreate(BaseModel):
    title: str | None = None


class ChatSessionResponse(BaseModel):
    id: uuid.UUID
    title: str | None
    status: str
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class ChatMessageSend(BaseModel):
    content: str


class ChatMessageResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    role: str
    content: str
    tokens_used: int | None
    created_at: datetime.datetime

    model_config = {"from_attributes": True}
