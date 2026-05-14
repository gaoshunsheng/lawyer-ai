from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case, CaseTimeline, Evidence


# ── Case ──

async def generate_case_number(db: AsyncSession, tenant_id: uuid.UUID) -> str:
    from datetime import datetime

    year = datetime.now().year
    stmt = select(func.count(Case.id)).where(
        Case.tenant_id == tenant_id,
        func.extract("year", Case.created_at) == year,
    )
    result = await db.execute(stmt)
    count = result.scalar() or 0
    return f"LD-{year}-{count + 1:04d}"


async def list_cases(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    case_type: str | None = None,
    lawyer_id: uuid.UUID | None = None,
    search: str | None = None,
) -> tuple[list[Case], int]:
    conditions = [Case.tenant_id == tenant_id]
    if status:
        conditions.append(Case.status == status)
    if case_type:
        conditions.append(Case.case_type == case_type)
    if lawyer_id:
        conditions.append(Case.lawyer_id == lawyer_id)
    if search:
        conditions.append(Case.title.ilike(f"%{search}%"))

    count_stmt = select(func.count(Case.id)).where(*conditions)
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = (
        select(Case)
        .where(*conditions)
        .order_by(Case.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    return items, total


async def get_case(db: AsyncSession, case_id: uuid.UUID) -> Case | None:
    stmt = select(Case).where(Case.id == case_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_case(db: AsyncSession, tenant_id: uuid.UUID, lawyer_id: uuid.UUID, data: dict) -> Case:
    case_number = await generate_case_number(db, tenant_id)
    case = Case(
        case_number=case_number,
        tenant_id=tenant_id,
        lawyer_id=lawyer_id,
        **data,
    )
    db.add(case)
    await db.flush()
    return case


async def update_case(db: AsyncSession, case: Case, data: dict) -> Case:
    for key, value in data.items():
        if value is not None:
            setattr(case, key, value)
    await db.flush()
    return case


async def update_case_status(db: AsyncSession, case: Case, status: str) -> Case:
    case.status = status
    await db.flush()
    return case


# ── Evidence ──

async def list_evidences(db: AsyncSession, case_id: uuid.UUID) -> list[Evidence]:
    stmt = (
        select(Evidence)
        .where(Evidence.case_id == case_id)
        .order_by(Evidence.sort_order, Evidence.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_evidence(db: AsyncSession, evidence_id: uuid.UUID) -> Evidence | None:
    stmt = select(Evidence).where(Evidence.id == evidence_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_evidence(
    db: AsyncSession,
    case_id: uuid.UUID,
    tenant_id: uuid.UUID,
    data: dict,
    file_url: str | None = None,
    file_size: int | None = None,
    file_type: str | None = None,
) -> Evidence:
    evidence = Evidence(
        case_id=case_id,
        tenant_id=tenant_id,
        file_url=file_url,
        file_size=file_size,
        file_type=file_type,
        **data,
    )
    db.add(evidence)
    await db.flush()
    return evidence


async def update_evidence(db: AsyncSession, evidence: Evidence, data: dict) -> Evidence:
    for key, value in data.items():
        if value is not None:
            setattr(evidence, key, value)
    await db.flush()
    return evidence


async def delete_evidence(db: AsyncSession, evidence: Evidence) -> None:
    await db.delete(evidence)
    await db.flush()


# ── Timeline ──

async def list_timelines(db: AsyncSession, case_id: uuid.UUID) -> list[CaseTimeline]:
    stmt = (
        select(CaseTimeline)
        .where(CaseTimeline.case_id == case_id)
        .order_by(CaseTimeline.event_date.desc(), CaseTimeline.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_timeline(db: AsyncSession, timeline_id: uuid.UUID) -> CaseTimeline | None:
    stmt = select(CaseTimeline).where(CaseTimeline.id == timeline_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_timeline(
    db: AsyncSession,
    case_id: uuid.UUID,
    created_by: uuid.UUID,
    data: dict,
) -> CaseTimeline:
    timeline = CaseTimeline(case_id=case_id, created_by=created_by, **data)
    db.add(timeline)
    await db.flush()
    return timeline


async def update_timeline(db: AsyncSession, timeline: CaseTimeline, data: dict) -> CaseTimeline:
    for key, value in data.items():
        if value is not None:
            setattr(timeline, key, value)
    await db.flush()
    return timeline


async def delete_timeline(db: AsyncSession, timeline: CaseTimeline) -> None:
    await db.delete(timeline)
    await db.flush()
