import uuid

from sqlalchemy import Boolean, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, BaseMixin


class ModelProvider(Base, BaseMixin):
    __tablename__ = "model_providers"

    name: Mapped[str] = mapped_column(String(100))
    api_base_url: Mapped[str] = mapped_column(String(500))
    api_key_encrypted: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="active")
    priority: Mapped[int] = mapped_column(Integer, default=0)


class ModelConfig(Base, BaseMixin):
    __tablename__ = "model_configs"

    provider_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    model_name: Mapped[str] = mapped_column(String(100))
    model_type: Mapped[str] = mapped_column(String(50))  # chat/embedding
    capability: Mapped[str | None] = mapped_column(String(50))  # router/consult/document/review/trial
    input_price_per_m: Mapped[float | None] = mapped_column(Numeric(10, 6))
    output_price_per_m: Mapped[float | None] = mapped_column(Numeric(10, 6))
    max_tokens: Mapped[int | None] = mapped_column(Integer)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default="active")
