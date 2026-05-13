import uuid

from sqlalchemy import Boolean, ForeignKey, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, BaseMixin


class ResponseFeedback(Base, BaseMixin):
    __tablename__ = "response_feedbacks"

    message_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chat_messages.id"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    overall_positive: Mapped[bool] = mapped_column(Boolean)
    law_accuracy_score: Mapped[int | None] = mapped_column(SmallInteger)
    analysis_depth_score: Mapped[int | None] = mapped_column(SmallInteger)
    practical_value_score: Mapped[int | None] = mapped_column(SmallInteger)
    text_feedback: Mapped[str | None] = mapped_column(Text)
    ai_analysis: Mapped[str | None] = mapped_column(Text)
