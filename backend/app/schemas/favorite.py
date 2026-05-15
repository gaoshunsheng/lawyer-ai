from __future__ import annotations

import datetime
import uuid
from pydantic import BaseModel, Field


VALID_TARGET_TYPES = ("case", "document", "law", "case_precedent")


class FavoriteCreate(BaseModel):
    target_type: str = Field(..., pattern="^(case|document|law|case_precedent)$")
    target_id: uuid.UUID
    notes: str | None = None


class FavoriteUpdate(BaseModel):
    notes: str | None = None


class FavoriteResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    target_type: str
    target_id: uuid.UUID
    notes: str | None
    created_at: datetime.datetime

    model_config = {"from_attributes": True}
