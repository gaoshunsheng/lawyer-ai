from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseMixin


class DocumentTemplate(Base, BaseMixin):
    __tablename__ = "document_templates"

    name: Mapped[str] = mapped_column(String(200))
    doc_type: Mapped[str] = mapped_column(String(50), index=True)
    content_template: Mapped[str] = mapped_column(Text)
    variables_schema: Mapped[dict] = mapped_column(JSONB, default=dict)
    category: Mapped[str] = mapped_column(String(50), index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), index=True)

    documents: Mapped[list["Document"]] = relationship("Document", back_populates="template")


class Document(Base, BaseMixin):
    __tablename__ = "documents"

    case_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"), index=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(200))
    doc_type: Mapped[str] = mapped_column(String(50))
    template_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("document_templates.id"))
    content: Mapped[dict | None] = mapped_column(JSONB)
    variables: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    version: Mapped[int] = mapped_column(Integer, default=1)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"))

    template: Mapped["DocumentTemplate | None"] = relationship("DocumentTemplate", back_populates="documents")
    parent: Mapped["Document | None"] = relationship("Document", remote_side="Document.id", back_populates="children")
    children: Mapped[list["Document"]] = relationship("Document", back_populates="parent")
