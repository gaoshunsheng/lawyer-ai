import uuid

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, BaseMixin


class Law(Base, BaseMixin):
    __tablename__ = "laws"

    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    title: Mapped[str] = mapped_column(String(500))
    law_type: Mapped[str] = mapped_column(String(50))  # law/regulation/judicial_interpretation/local
    promulgating_body: Mapped[str | None] = mapped_column(String(200))
    promulgation_date: Mapped[object | None] = mapped_column(Date)
    effective_date: Mapped[object | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="effective")
    full_text: Mapped[str] = mapped_column(Text)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)


class LawArticle(Base, BaseMixin):
    __tablename__ = "law_articles"

    law_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("laws.id"), index=True)
    article_number: Mapped[str] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(Text)
    chapter: Mapped[str | None] = mapped_column(String(200))


class PrecedentCase(Base, BaseMixin):
    __tablename__ = "precedent_cases"

    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    case_name: Mapped[str] = mapped_column(String(500))
    case_type: Mapped[str | None] = mapped_column(String(50))
    court: Mapped[str | None] = mapped_column(String(200))
    court_level: Mapped[str | None] = mapped_column(String(50))
    procedure: Mapped[str | None] = mapped_column(String(50))  # first/second/retrial
    judgment_date: Mapped[object | None] = mapped_column(Date)
    region: Mapped[str | None] = mapped_column(String(100))
    result: Mapped[str | None] = mapped_column(String(50))  # win/lose/partial
    summary: Mapped[str | None] = mapped_column(Text)
    full_text: Mapped[str] = mapped_column(Text)
    key_points: Mapped[dict | None] = mapped_column(JSONB)
