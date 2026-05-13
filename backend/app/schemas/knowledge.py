import datetime
import uuid

from pydantic import BaseModel


class LawResponse(BaseModel):
    id: uuid.UUID
    title: str
    law_type: str
    promulgating_body: str | None
    promulgation_date: datetime.date | None
    effective_date: datetime.date | None
    status: str

    model_config = {"from_attributes": True}


class LawArticleResponse(BaseModel):
    id: uuid.UUID
    law_id: uuid.UUID
    article_number: str
    content: str
    chapter: str | None

    model_config = {"from_attributes": True}


class LawDetailResponse(LawResponse):
    full_text: str
    articles: list[LawArticleResponse] = []


class CaseResponse(BaseModel):
    id: uuid.UUID
    case_name: str
    case_type: str | None
    court: str | None
    court_level: str | None
    procedure: str | None
    judgment_date: datetime.date | None
    region: str | None
    result: str | None
    summary: str | None

    model_config = {"from_attributes": True}


class CaseDetailResponse(CaseResponse):
    full_text: str
    key_points: dict | None


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
