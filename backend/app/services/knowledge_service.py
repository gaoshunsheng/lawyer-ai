"""知识库服务 - 法规/案例 CRUD + 向量化"""

import uuid

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Law, LawArticle, PrecedentCase


async def list_laws(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID | None = None,
    law_type: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Law], int]:
    query = select(Law)
    count_query = select(func.count(Law.id))

    if tenant_id:
        condition = or_(Law.tenant_id == tenant_id, Law.tenant_id.is_(None))
        query = query.where(condition)
        count_query = count_query.where(condition)

    if law_type:
        query = query.where(Law.law_type == law_type)
        count_query = count_query.where(Law.law_type == law_type)

    if keyword:
        keyword_filter = Law.title.ilike(f"%{keyword}%")
        query = query.where(keyword_filter)
        count_query = count_query.where(keyword_filter)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Law.effective_date.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    laws = result.scalars().all()

    return list(laws), total


async def get_law(db: AsyncSession, law_id: uuid.UUID) -> Law | None:
    result = await db.execute(select(Law).where(Law.id == law_id))
    return result.scalar_one_or_none()


async def get_law_articles(db: AsyncSession, law_id: uuid.UUID) -> list[LawArticle]:
    result = await db.execute(
        select(LawArticle).where(LawArticle.law_id == law_id).order_by(LawArticle.article_number)
    )
    return list(result.scalars().all())


async def list_cases(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID | None = None,
    case_type: str | None = None,
    court: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[PrecedentCase], int]:
    query = select(PrecedentCase)
    count_query = select(func.count(PrecedentCase.id))

    if tenant_id:
        condition = or_(PrecedentCase.tenant_id == tenant_id, PrecedentCase.tenant_id.is_(None))
        query = query.where(condition)
        count_query = count_query.where(condition)

    if case_type:
        query = query.where(PrecedentCase.case_type == case_type)
        count_query = count_query.where(PrecedentCase.case_type == case_type)

    if court:
        query = query.where(PrecedentCase.court.ilike(f"%{court}%"))
        count_query = count_query.where(PrecedentCase.court.ilike(f"%{court}%"))

    if keyword:
        keyword_filter = PrecedentCase.case_name.ilike(f"%{keyword}%")
        query = query.where(keyword_filter)
        count_query = count_query.where(keyword_filter)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(PrecedentCase.judgment_date.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    cases = result.scalars().all()

    return list(cases), total


async def get_case(db: AsyncSession, case_id: uuid.UUID) -> PrecedentCase | None:
    result = await db.execute(select(PrecedentCase).where(PrecedentCase.id == case_id))
    return result.scalar_one_or_none()
