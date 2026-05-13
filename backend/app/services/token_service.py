import uuid
from datetime import date, datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Department, Tenant, TokenUsage, TokenUsageDaily, User


async def record_usage(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    department_id: uuid.UUID | None,
    user_id: uuid.UUID,
    session_id: uuid.UUID | None = None,
    model_provider: str = "zhipu",
    model_name: str = "glm-5-turbo",
    agent_type: str | None = None,
    input_tokens: int = 0,
    output_tokens: int = 0,
    total_tokens: int = 0,
    latency_ms: int | None = None,
    cost_cny: float | None = None,
) -> TokenUsage:
    usage = TokenUsage(
        tenant_id=tenant_id,
        department_id=department_id,
        user_id=user_id,
        session_id=session_id,
        model_provider=model_provider,
        model_name=model_name,
        agent_type=agent_type,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        latency_ms=latency_ms,
        cost_cny=cost_cny,
    )
    db.add(usage)
    await db.flush()

    # Upsert daily aggregation
    today = date.today()
    await _upsert_daily(db, today, tenant_id, department_id, user_id, model_name, agent_type, input_tokens, output_tokens, total_tokens, cost_cny or 0)

    return usage


async def _upsert_daily(
    db: AsyncSession,
    target_date: date,
    tenant_id: uuid.UUID,
    department_id: uuid.UUID | None,
    user_id: uuid.UUID | None,
    model_name: str,
    agent_type: str | None,
    input_tokens: int,
    output_tokens: int,
    total_tokens: int,
    cost_cny: float,
) -> None:
    result = await db.execute(
        select(TokenUsageDaily).where(
            TokenUsageDaily.date == target_date,
            TokenUsageDaily.tenant_id == tenant_id,
            TokenUsageDaily.department_id == department_id if department_id else TokenUsageDaily.department_id.is_(None),
            TokenUsageDaily.user_id == user_id if user_id else TokenUsageDaily.user_id.is_(None),
            TokenUsageDaily.model_name == model_name,
            TokenUsageDaily.agent_type == agent_type if agent_type else TokenUsageDaily.agent_type.is_(None),
        )
    )
    daily = result.scalar_one_or_none()
    if daily:
        daily.total_input_tokens += input_tokens
        daily.total_output_tokens += output_tokens
        daily.total_tokens += total_tokens
        daily.total_cost_cny = (daily.total_cost_cny or 0) + cost_cny
        daily.request_count += 1
    else:
        daily = TokenUsageDaily(
            id=uuid.uuid4(),
            date=target_date,
            tenant_id=tenant_id,
            department_id=department_id,
            user_id=user_id,
            model_name=model_name,
            agent_type=agent_type,
            total_input_tokens=input_tokens,
            total_output_tokens=output_tokens,
            total_tokens=total_tokens,
            total_cost_cny=cost_cny,
            request_count=1,
        )
        db.add(daily)
    await db.flush()


async def check_budget(db: AsyncSession, user_id: uuid.UUID) -> tuple[bool, str | None]:
    """Check user → department → tenant budget cascade. Returns (allowed, reason)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return False, "用户不存在"

    # Check user budget
    if user.token_budget_monthly is not None:
        usage = await _get_monthly_usage(db, user_id=user.id)
        if usage >= user.token_budget_monthly:
            return False, "个人Token预算已耗尽"

    # Check department budget
    if user.department_id:
        dept_result = await db.execute(select(Department).where(Department.id == user.department_id))
        dept = dept_result.scalar_one_or_none()
        if dept and dept.token_budget_monthly is not None:
            usage = await _get_monthly_usage(db, department_id=dept.id)
            if usage >= dept.token_budget_monthly:
                return False, "部门Token预算已耗尽"

    # Check tenant budget
    tenant_result = await db.execute(select(Tenant).where(Tenant.id == user.tenant_id))
    tenant = tenant_result.scalar_one_or_none()
    if tenant and tenant.token_budget_monthly is not None:
        usage = await _get_monthly_usage(db, tenant_id=tenant.id)
        if usage >= tenant.token_budget_monthly:
            return False, "律所Token预算已耗尽"

    return True, None


async def _get_monthly_usage(db: AsyncSession, *, tenant_id: uuid.UUID | None = None, department_id: uuid.UUID | None = None, user_id: uuid.UUID | None = None) -> int:
    today = date.today()
    month_start = date(today.year, today.month, 1)
    query = select(func.coalesce(func.sum(TokenUsageDaily.total_tokens), 0)).where(TokenUsageDaily.date >= month_start)
    if tenant_id:
        query = query.where(TokenUsageDaily.tenant_id == tenant_id)
    if department_id:
        query = query.where(TokenUsageDaily.department_id == department_id)
    if user_id:
        query = query.where(TokenUsageDaily.user_id == user_id)
    result = await db.execute(query)
    return result.scalar() or 0
