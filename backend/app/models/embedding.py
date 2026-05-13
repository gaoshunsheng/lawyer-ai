import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import Index, String, Text
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
    embedding = mapped_column(Vector(1536))
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)

    __table_args__ = (
        Index(
            "ix_law_embeddings_hnsw",
            embedding,
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )


class CaseEmbedding(Base, BaseMixin):
    __tablename__ = "case_embeddings"

    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    chunk_text: Mapped[str] = mapped_column(Text)
    chunk_type: Mapped[str] = mapped_column(String(20), default="ruling")
    embedding = mapped_column(Vector(1536))
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)

    __table_args__ = (
        Index(
            "ix_case_embeddings_hnsw",
            embedding,
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )
