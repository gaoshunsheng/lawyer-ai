# backend/app/services/feedback_service.py
from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta

from sqlalchemy import func, select, case, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.feedback import ResponseFeedback


async def get_feedback_stats(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    days: int = 30,
) -> dict:
    """Aggregate feedback stats for the last N days."""
    cutoff = datetime.now() - timedelta(days=days)

    base_condition = [
        ResponseFeedback.tenant_id == tenant_id,
        ResponseFeedback.created_at >= cutoff,
    ]

    # Total count
    count_stmt = select(func.count(ResponseFeedback.id)).where(*base_condition)
    total = (await db.execute(count_stmt)).scalar() or 0

    if total == 0:
        return {
            "total": 0,
            "positive_rate": 0,
            "negative_rate": 0,
            "avg_law_accuracy": 0,
            "avg_analysis_depth": 0,
            "avg_practical_value": 0,
        }

    # Positive rate
    pos_stmt = select(func.count(ResponseFeedback.id)).where(
        *base_condition,
        ResponseFeedback.overall_positive == True,
    )
    positive_count = (await db.execute(pos_stmt)).scalar() or 0

    # Average scores
    avg_stmt = select(
        func.avg(ResponseFeedback.law_accuracy_score).label("avg_law"),
        func.avg(ResponseFeedback.analysis_depth_score).label("avg_depth"),
        func.avg(ResponseFeedback.practical_value_score).label("avg_value"),
    ).where(*base_condition)
    avg_result = (await db.execute(avg_stmt)).one()

    return {
        "total": total,
        "positive_rate": round(positive_count / total * 100, 1),
        "negative_rate": round((total - positive_count) / total * 100, 1),
        "avg_law_accuracy": round(avg_result.avg_law or 0, 2),
        "avg_analysis_depth": round(avg_result.avg_depth or 0, 2),
        "avg_practical_value": round(avg_result.avg_value or 0, 2),
    }


async def get_feedback_trends(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    days: int = 30,
    granularity: str = "day",
) -> list[dict]:
    """Get daily/weekly/monthly satisfaction trends."""
    cutoff = datetime.now() - timedelta(days=days)

    if granularity == "month":
        date_col = func.date_trunc("month", ResponseFeedback.created_at)
    elif granularity == "week":
        date_col = func.date_trunc("week", ResponseFeedback.created_at)
    else:
        date_col = func.date_trunc("day", ResponseFeedback.created_at)

    stmt = (
        select(
            date_col.label("period"),
            func.count(ResponseFeedback.id).label("total"),
            func.sum(case((ResponseFeedback.overall_positive == True, 1), else_=0)).label("positive"),
        )
        .where(
            ResponseFeedback.tenant_id == tenant_id,
            ResponseFeedback.created_at >= cutoff,
        )
        .group_by("period")
        .order_by("period")
    )

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "period": str(row.period),
            "total": row.total,
            "positive": row.positive or 0,
            "negative": row.total - (row.positive or 0),
            "satisfaction_rate": round((row.positive or 0) / row.total * 100, 1) if row.total > 0 else 0,
        }
        for row in rows
    ]
