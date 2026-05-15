import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models import Law, PrecedentCase, User
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


# ── AI Law Interpretation (SSE) ──


@router.post("/laws/{law_id}/interpret")
async def interpret_law(
    law_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    law = await get_law(db, law_id)
    if not law:
        raise HTTPException(status_code=404, detail="法规不存在")

    articles = await get_law_articles(db, law_id)

    from app.ai.graphs._client import get_openai_client
    client = get_openai_client()

    articles_text = "\n".join([
        f"第{a.article_number}条 {a.content}"
        for a in articles[:20]
    ])
    total_articles = len(articles)

    async def event_stream():
        yield f"data: {json.dumps({'status': 'analyzing', 'message': '正在分析法规...'})}\n\n"

        prompt = f"""请对以下法规进行专业解读：

法规名称：{law.title}
法规类型：{law.law_type}
颁布机构：{law.promulgating_body or '未知'}
生效日期：{law.effective_date or '未知'}

条款内容：
{articles_text if articles_text else '暂无法条数据'}
{"（仅展示前20条，共" + str(total_articles) + "条）" if total_articles > 20 else ""}

请按以下结构输出解读（markdown格式）：
1. 法规概述（立法目的、适用范围）
2. 核心条款解读（逐条分析关键条款的含义和实践应用）
3. 实务影响（对劳动关系的实际影响）
4. 注意事项（实践中需特别注意的问题）
5. 相关法规（列出相关的配套法规或司法解释）"""

        response = await client.chat.completions.create(
            model="glm-5-turbo",
            messages=[
                {"role": "system", "content": "你是一位资深劳动法律师，擅长用通俗易懂的语言解读法律条文。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=4096,
            stream=True,
        )

        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ── Batch Import (Admin Only) ──


class BatchImportRequest(BaseModel):
    laws: list[dict] = []
    cases: list[dict] = []


@router.post("/import")
async def batch_import(
    req: BatchImportRequest,
    current_user: User = Depends(require_role("platform_admin", "tenant_admin")),
    db: AsyncSession = Depends(get_db),
):
    imported = {"laws": 0, "cases": 0, "errors": []}

    for law_data in req.laws:
        try:
            async with db.begin_nested():
                law = Law(
                    tenant_id=current_user.tenant_id,
                    title=law_data.get("title", ""),
                    law_type=law_data.get("law_type", "law"),
                    promulgating_body=law_data.get("promulgating_body"),
                    promulgation_date=law_data.get("publish_date"),
                    effective_date=law_data.get("effective_date"),
                    status=law_data.get("status", "effective"),
                    full_text=law_data.get("full_text", ""),
                )
                db.add(law)
                imported["laws"] += 1
        except Exception as e:
            imported["errors"].append(f"导入法规失败: {str(e)}")

    for case_data in req.cases:
        try:
            async with db.begin_nested():
                case = PrecedentCase(
                    tenant_id=current_user.tenant_id,
                    case_name=case_data.get("case_name", ""),
                    case_type=case_data.get("case_type"),
                    case_number=case_data.get("case_number"),
                    court=case_data.get("court"),
                    judgment_date=case_data.get("judgment_date"),
                    plaintiff=case_data.get("plaintiff"),
                    defendant=case_data.get("defendant"),
                    result=case_data.get("result"),
                    summary=case_data.get("summary"),
                    full_text=case_data.get("full_text"),
                )
                db.add(case)
                imported["cases"] += 1
        except Exception as e:
            imported["errors"].append(f"导入案例失败: {str(e)}")

    await db.flush()
    return imported
