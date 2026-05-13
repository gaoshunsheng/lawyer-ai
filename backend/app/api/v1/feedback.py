import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import ResponseFeedback, User

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackRequest(BaseModel):
    message_id: uuid.UUID
    overall_positive: bool
    law_accuracy_score: int | None = None
    analysis_depth_score: int | None = None
    practical_value_score: int | None = None
    text_feedback: str | None = None


@router.post("/", status_code=201)
async def create_feedback(
    req: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    fb = ResponseFeedback(
        message_id=req.message_id,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        overall_positive=req.overall_positive,
        law_accuracy_score=req.law_accuracy_score,
        analysis_depth_score=req.analysis_depth_score,
        practical_value_score=req.practical_value_score,
        text_feedback=req.text_feedback,
    )
    db.add(fb)
    return {"status": "ok"}
