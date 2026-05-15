from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import ARRAY, Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseMixin


class Case(Base, BaseMixin):
    __tablename__ = "cases"

    case_number: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    case_type: Mapped[str] = mapped_column(String(50), index=True)
    status: Mapped[str] = mapped_column(String(20), index=True, default="pending")
    plaintiff: Mapped[dict] = mapped_column(JSONB, default=dict)
    defendant: Mapped[dict] = mapped_column(JSONB, default=dict)
    claim_amount: Mapped[float | None] = mapped_column(Numeric(12, 2))
    dispute_focus: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    lawyer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    assistant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    gantt_data: Mapped[dict | None] = mapped_column(JSONB)
    ai_analysis: Mapped[dict | None] = mapped_column(JSONB)

    lawyer: Mapped["User"] = relationship("User", foreign_keys=[lawyer_id])
    assistant: Mapped["User | None"] = relationship("User", foreign_keys=[assistant_id])
    evidences: Mapped[list["Evidence"]] = relationship("Evidence", back_populates="case", cascade="all, delete-orphan")
    timelines: Mapped[list["CaseTimeline"]] = relationship("CaseTimeline", back_populates="case", cascade="all, delete-orphan")


class Evidence(Base, BaseMixin):
    __tablename__ = "evidences"

    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"), index=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    evidence_type: Mapped[str] = mapped_column(String(50))
    file_url: Mapped[str | None] = mapped_column(String(500))
    file_size: Mapped[int | None] = mapped_column(Integer)
    file_type: Mapped[str | None] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    case: Mapped["Case"] = relationship("Case", back_populates="evidences")


class CaseTimeline(Base, BaseMixin):
    __tablename__ = "case_timelines"

    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(20))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    event_date: Mapped[date] = mapped_column(Date)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    case: Mapped["Case"] = relationship("Case", back_populates="timelines")
