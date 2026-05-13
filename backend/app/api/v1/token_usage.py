import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models import TokenUsageDaily, User
from app.schemas.token_usage import BudgetStatus, ModelConfigResponse, TokenUsageDailyResponse
from app.services.token_service import _get_monthly_usage

router = APIRouter(prefix="/token-usage", tags=["token-usage"])


@router.get("/daily", response_model=list[TokenUsageDailyResponse])
async def get_daily_usage(
    start_date: date = Query(...),
    end_date: date = Query(...),
    user_id: uuid.UUID | None = None,
    department_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(TokenUsageDaily).where(
        TokenUsageDaily.tenant_id == current_user.tenant_id,
        TokenUsageDaily.date >= start_date,
        TokenUsageDaily.date <= end_date,
    )
    if user_id:
        query = query.where(TokenUsageDaily.user_id == user_id)
    if department_id:
        query = query.where(TokenUsageDaily.department_id == department_id)

    result = await db.execute(query.order_by(TokenUsageDaily.date.desc()))
    return result.scalars().all()


@router.get("/budget", response_model=list[BudgetStatus])
async def get_budget_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    budgets = []

    # User budget
    if current_user.token_budget_monthly is not None:
        used = await _get_monthly_usage(db, user_id=current_user.id)
        budgets.append(BudgetStatus(
            entity_type="user",
            entity_id=current_user.id,
            budget=current_user.token_budget_monthly,
            used=used,
            remaining=current_user.token_budget_monthly - used,
            percentage=round(used / current_user.token_budget_monthly * 100, 1) if current_user.token_budget_monthly else None,
        ))

    # Department budget
    if current_user.department_id:
        from app.models import Department
        dept_result = await db.execute(select(Department).where(Department.id == current_user.department_id))
        dept = dept_result.scalar_one_or_none()
        if dept and dept.token_budget_monthly is not None:
            used = await _get_monthly_usage(db, department_id=dept.id)
            budgets.append(BudgetStatus(
                entity_type="department",
                entity_id=dept.id,
                budget=dept.token_budget_monthly,
                used=used,
                remaining=dept.token_budget_monthly - used,
                percentage=round(used / dept.token_budget_monthly * 100, 1),
            ))

    # Tenant budget
    from app.models import Tenant
    tenant_result = await db.execute(select(Tenant).where(Tenant.id == current_user.tenant_id))
    tenant = tenant_result.scalar_one_or_none()
    if tenant and tenant.token_budget_monthly is not None:
        used = await _get_monthly_usage(db, tenant_id=tenant.id)
        budgets.append(BudgetStatus(
            entity_type="tenant",
            entity_id=tenant.id,
            budget=tenant.token_budget_monthly,
            used=used,
            remaining=tenant.token_budget_monthly - used,
            percentage=round(used / tenant.token_budget_monthly * 100, 1),
        ))

    return budgets
