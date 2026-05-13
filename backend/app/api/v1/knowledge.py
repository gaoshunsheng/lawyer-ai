import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.knowledge import (
    CaseDetailResponse,
    CaseResponse,
    LawArticleResponse,
    LawDetailResponse,
    LawResponse,
    PaginatedResponse,
)
from app.services.knowledge_service import (
    get_case,
    get_law,
    get_law_articles,
    list_cases,
    list_laws,
)

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("/laws", response_model=PaginatedResponse)
async def search_laws(
    keyword: str | None = None,
    law_type: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    laws, total = await list_laws(
        db, tenant_id=current_user.tenant_id, law_type=law_type, keyword=keyword, page=page, page_size=page_size
    )
    return PaginatedResponse(
        items=[LawResponse.model_validate(law) for law in laws],
        total=total, page=page, page_size=page_size,
    )


@router.get("/laws/{law_id}", response_model=LawDetailResponse)
async def get_law_detail(
    law_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    law = await get_law(db, law_id)
    if not law:
        raise HTTPException(status_code=404, detail="法规不存在")
    articles = await get_law_articles(db, law_id)
    return LawDetailResponse(
        **LawResponse.model_validate(law).model_dump(),
        full_text=law.full_text,
        articles=[LawArticleResponse.model_validate(a) for a in articles],
    )


@router.get("/cases", response_model=PaginatedResponse)
async def search_cases(
    keyword: str | None = None,
    case_type: str | None = None,
    court: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cases, total = await list_cases(
        db, tenant_id=current_user.tenant_id, case_type=case_type, court=court, keyword=keyword, page=page, page_size=page_size
    )
    return PaginatedResponse(
        items=[CaseResponse.model_validate(case) for case in cases],
        total=total, page=page, page_size=page_size,
    )


@router.get("/cases/{case_id}", response_model=CaseDetailResponse)
async def get_case_detail(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = await get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="案例不存在")
    return CaseDetailResponse(
        **CaseResponse.model_validate(case).model_dump(),
        full_text=case.full_text,
        key_points=case.key_points,
    )
