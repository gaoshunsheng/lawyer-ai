from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case


async def get_case_overview(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> dict:
    conditions = [Case.tenant_id == tenant_id]
    if start_date:
        conditions.append(Case.created_at >= start_date)
    if end_date:
        conditions.append(Case.created_at <= end_date)

    total = (await db.execute(select(func.count(Case.id)).where(*conditions))).scalar() or 0

    type_rows = (
        await db.execute(
            select(
                Case.case_type.label("type"),
                func.count(Case.id).label("count"),
                func.coalesce(func.sum(Case.claim_amount), 0).label("amount"),
            )
            .where(*conditions)
            .group_by(Case.case_type)
        )
    ).all()

    status_rows = (
        await db.execute(
            select(Case.status.label("status"), func.count(Case.id).label("count"))
            .where(*conditions)
            .group_by(Case.status)
        )
    ).all()

    closed = (
        await db.execute(select(func.count(Case.id)).where(*conditions, Case.status == "closed"))
    ).scalar() or 0

    avg_dur = (
        await db.execute(
            select(func.avg(extract("day", Case.updated_at - Case.created_at)))
            .where(*conditions, Case.status == "closed")
        )
    ).scalar() or 0

    total_amount = float(
        (await db.execute(select(func.coalesce(func.sum(Case.claim_amount), 0)).where(*conditions))).scalar() or 0
    )

    return {
        "total": total,
        "by_type": [{"type": r.type, "count": r.count, "amount": float(r.amount)} for r in type_rows],
        "by_status": [{"status": r.status, "count": r.count} for r in status_rows],
        "avg_duration_days": round(float(avg_dur), 1),
        "win_rate": round(closed / total * 100, 1) if total > 0 else 0,
        "total_claim_amount": total_amount,
    }


async def get_trends(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    granularity: str = "month",
    days: int = 180,
) -> dict:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    if granularity == "quarter":
        date_col = func.date_trunc("quarter", Case.created_at)
    else:
        date_col = func.date_trunc("month", Case.created_at)

    rows = (
        await db.execute(
            select(
                date_col.label("period"),
                func.count(Case.id).label("total"),
                func.coalesce(func.avg(Case.claim_amount), 0).label("avg_amount"),
            )
            .where(Case.tenant_id == tenant_id, Case.created_at >= cutoff)
            .group_by("period")
            .order_by("period")
        )
    ).all()

    return {
        "periods": [
            {
                "period": str(r.period)[:10] if r.period else "",
                "total": r.total,
                "by_type": {},
                "avg_amount": float(r.avg_amount),
            }
            for r in rows
        ]
    }


async def get_lawyer_performance(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    period_days: int = 90,
) -> dict:
    cutoff = datetime.now(timezone.utc) - timedelta(days=period_days)
    rows = (
        await db.execute(
            select(
                Case.lawyer_id.label("user_id"),
                func.count(Case.id).label("total_cases"),
                func.coalesce(func.sum(Case.claim_amount), 0).label("total_amount"),
            )
            .where(Case.tenant_id == tenant_id, Case.created_at >= cutoff)
            .group_by(Case.lawyer_id)
            .order_by(func.count(Case.id).desc())
        )
    ).all()

    from app.models import User
    lawyers = []
    for r in rows:
        name_row = await db.execute(select(User.real_name).where(User.id == r.user_id))
        name = name_row.scalar() or "未知"
        lawyers.append({
            "user_id": str(r.user_id),
            "name": name,
            "total_cases": r.total_cases,
            "win_rate": 0.0,
            "avg_satisfaction": 0.0,
            "total_claim_amount": float(r.total_amount),
        })
    return {"lawyers": lawyers, "period_days": period_days}
