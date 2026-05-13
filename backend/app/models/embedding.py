import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, BaseMixin


class LawEmbedding(Base, BaseMixin):
    __tablename__ = "law_embeddings"

    law_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    article_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    article_number: Mapped[str | None] = mapped_column(String(50))
    chunk_text: Mapped[str] = mapped_column(Text)
    chunk_type: Mapped[str] = mapped_column(String(20), default="article")
    embedding = mapped_column(Vector(2048))
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)


class CaseEmbedding(Base, BaseMixin):
    __tablename__ = "case_embeddings"

    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    chunk_text: Mapped[str] = mapped_column(Text)
    chunk_type: Mapped[str] = mapped_column(String(20), default="ruling")
    embedding = mapped_column(Vector(2048))
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)
