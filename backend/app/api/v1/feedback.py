import uuid

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
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


@router.get("/stats")
async def get_feedback_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_role("platform_admin", "tenant_admin")),
    db: AsyncSession = Depends(get_db),
):
    from app.services import feedback_service as fb_service

    stats = await fb_service.get_feedback_stats(db, current_user.tenant_id, days)
    return stats


@router.get("/trends")
async def get_feedback_trends(
    days: int = Query(30, ge=1, le=365),
    granularity: str = Query("day", pattern="^(day|week|month)$"),
    current_user: User = Depends(require_role("platform_admin", "tenant_admin")),
    db: AsyncSession = Depends(get_db),
):
    from app.services import feedback_service as fb_service

    trends = await fb_service.get_feedback_trends(db, current_user.tenant_id, days, granularity)
    return trends
