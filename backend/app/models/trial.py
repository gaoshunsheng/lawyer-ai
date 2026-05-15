from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseMixin


class TrialSimulation(Base, BaseMixin):
    __tablename__ = "trial_simulations"

    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"), index=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    mode: Mapped[str] = mapped_column(String(20))
    role: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="active")
    rounds_completed: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    dispute_focus: Mapped[dict | None] = mapped_column(JSONB)
    strategy_report: Mapped[dict | None] = mapped_column(JSONB)

    rounds: Mapped[list["TrialRound"]] = relationship("TrialRound", back_populates="simulation", cascade="all, delete-orphan")


class TrialRound(Base, BaseMixin):
    __tablename__ = "trial_rounds"

    simulation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("trial_simulations.id"), index=True)
    round_num: Mapped[int] = mapped_column(Integer)
    role: Mapped[str] = mapped_column(String(10))
    content: Mapped[str] = mapped_column(Text)
    argument_strength: Mapped[str | None] = mapped_column(String(10))
    evaluation: Mapped[dict | None] = mapped_column(JSONB)

    simulation: Mapped["TrialSimulation"] = relationship("TrialSimulation", back_populates="rounds")
