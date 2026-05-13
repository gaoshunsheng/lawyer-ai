from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, SmallInteger, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseMixin


class Tenant(Base, BaseMixin):
    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(200))
    plan: Mapped[str] = mapped_column(String(20), default="free")  # free/pro/team/enterprise
    status: Mapped[str] = mapped_column(String(20), default="active")  # active/suspended/cancelled
    settings: Mapped[dict] = mapped_column(JSONB, default=dict)
    token_budget_monthly: Mapped[int | None] = mapped_column(BigInteger)

    departments: Mapped[list[Department]] = relationship(back_populates="tenant")
    users: Mapped[list["User"]] = relationship(back_populates="tenant")


class Department(Base, BaseMixin):
    __tablename__ = "departments"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id"))
    name: Mapped[str] = mapped_column(String(200))
    path: Mapped[str | None] = mapped_column(String(500))
    level: Mapped[int] = mapped_column(SmallInteger, default=0)
    settings: Mapped[dict] = mapped_column(JSONB, default=dict)
    token_budget_monthly: Mapped[int | None] = mapped_column(BigInteger)

    tenant: Mapped[Tenant] = relationship(back_populates="departments")
    parent: Mapped[Department | None] = relationship(remote_side="Department.id", back_populates="children")
    children: Mapped[list[Department]] = relationship(back_populates="parent")
