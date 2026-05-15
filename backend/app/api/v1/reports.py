from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models import User
from app.services import report_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/case-overview")
async def case_overview(
    days: int = Query(90, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    start = datetime.now(timezone.utc) - timedelta(days=days)
    return await report_service.get_case_overview(db, current_user.tenant_id, start)


@router.get("/trends")
async def trends(
    granularity: str = Query("month", pattern="^(month|quarter)$"),
    days: int = Query(180, ge=30, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await report_service.get_trends(db, current_user.tenant_id, granularity, days)


@router.get("/lawyer-performance")
async def lawyer_performance(
    period_days: int = Query(90, ge=30, le=365),
    current_user: User = Depends(require_role("platform_admin", "tenant_admin")),
    db: AsyncSession = Depends(get_db),
):
    return await report_service.get_lawyer_performance(db, current_user.tenant_id, period_days)


@router.get("/export")
async def export_report(
    format: str = Query("xlsx", pattern="^(xlsx|pdf)$"),
    report_type: str = Query("case_overview"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    raise NotImplementedError("导出功能待实现")
