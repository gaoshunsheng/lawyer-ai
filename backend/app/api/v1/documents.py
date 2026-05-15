# backend/app/api/v1/documents.py
from __future__ import annotations

import html
import json
import re
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.document import (
    BatchGenerateRequest,
    DocumentCreate,
    DocumentGenerateRequest,
    DocumentListResponse,
    DocumentResponse,
    DocumentUpdate,
    TemplateResponse,
    VersionDiffResponse,
)
from app.services import document_service

router = APIRouter(tags=["documents"])


# ── Templates ──

template_router = APIRouter(prefix="/document-templates")


@template_router.get("", response_model=list[TemplateResponse])
async def list_templates(
    category: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await document_service.list_templates(db, category, current_user.tenant_id)
    return [TemplateResponse.model_validate(i) for i in items]


@template_router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tmpl = await document_service.get_template(db, template_id)
    if not tmpl:
        raise HTTPException(status_code=404, detail="模板不存在")
    return TemplateResponse.model_validate(tmpl)


# ── Documents ──

doc_router = APIRouter(prefix="/documents")


@doc_router.get("", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    case_id: uuid.UUID | None = None,
    status: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await document_service.list_documents(
        db, current_user.tenant_id, page, page_size, case_id, status
    )
    return DocumentListResponse(
        items=[DocumentResponse.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@doc_router.post("", response_model=DocumentResponse, status_code=201)
async def create_document(
    req: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data = req.model_dump(exclude_unset=True)
    template_id = req.template_id

    content = None
    if template_id:
        tmpl = await document_service.get_template(db, template_id)
        if not tmpl:
            raise HTTPException(status_code=404, detail="模板不存在")
        if req.variables:
            content = {"raw": tmpl.content_template, "variables": req.variables}
        else:
            content = {"raw": tmpl.content_template}

    doc = await document_service.create_document(db, current_user.tenant_id, current_user.id, data, content)
    return DocumentResponse.model_validate(doc)


@doc_router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await document_service.get_document(db, doc_id)
    if not doc or doc.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="文书不存在")
    return DocumentResponse.model_validate(doc)


@doc_router.put("/{doc_id}", response_model=DocumentResponse)
async def update_document(
    doc_id: uuid.UUID,
    req: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await document_service.get_document(db, doc_id)
    if not doc or doc.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="文书不存在")
    doc = await document_service.update_document(db, doc, req.model_dump(exclude_unset=True))
    return DocumentResponse.model_validate(doc)


@doc_router.post("/{doc_id}/generate")
async def generate_document(
    doc_id: uuid.UUID,
    req: DocumentGenerateRequest | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await document_service.get_document(db, doc_id)
    if not doc or doc.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="文书不存在")

    async def event_stream():
        import asyncio
        yield f"data: {json.dumps({'status': 'generating', 'message': '正在生成文书...'})}\n\n"
        await asyncio.sleep(0.5)
        # Placeholder for actual AI generation — will be wired to Document Agent in Module 3
        if doc.content and doc.content.get("raw"):
            text = doc.content["raw"]
            if doc.content.get("variables"):
                for k, v in doc.content["variables"].items():
                    text = text.replace(f"{{{{{k}}}}}", str(v))
            yield f"data: {json.dumps({'status': 'complete', 'content': {'html': f'<pre>{html.escape(text)}</pre>'}})}\n\n"
        else:
            yield f"data: {json.dumps({'status': 'error', 'message': '无可用的模板内容'})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@doc_router.post("/{doc_id}/export")
async def export_document(
    doc_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await document_service.get_document(db, doc_id)
    if not doc or doc.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="文书不存在")

    # Placeholder: returns plain text; full Word/PDF export deferred
    text = doc.content.get("raw", "") if doc.content else ""
    if doc.content and doc.content.get("variables"):
        for k, v in doc.content["variables"].items():
            text = text.replace(f"{{{{{k}}}}}", str(v))

    from fastapi.responses import PlainTextResponse
    from urllib.parse import quote

    safe_title = re.sub(r'[\r\n]', '_', doc.title or "document")
    encoded_title = quote(safe_title)
    return PlainTextResponse(
        content=text,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_title}.txt"},
    )


# ── AI Smart Suggest (Stub) ──
# NOTE: This endpoint returns rule-based suggestions only, not AI-generated analysis.
# Full AI integration via document_graph is planned for a future iteration.


@doc_router.post("/{doc_id}/smart-suggest")
async def smart_suggest(
    doc_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await document_service.get_document(db, doc_id)
    if not doc or doc.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="文书不存在")

    content_text = ""
    if doc.content and doc.content.get("raw"):
        content_text = doc.content["raw"]

    suggestions = {
        "missing_clauses": [],
        "weak_arguments": [],
        "law_references": [],
        "format_issues": [],
    }

    if "《劳动法》" in content_text and "《劳动合同法》" not in content_text:
        suggestions["law_references"].append({
            "issue": "仅引用了《劳动法》，建议同时引用《劳动合同法》",
            "severity": "medium",
        })

    if "第" not in content_text:
        suggestions["weak_arguments"].append({
            "issue": "缺少具体法条引用，建议补充法条编号",
            "severity": "high",
        })

    return {"document_id": str(doc_id), "suggestions": suggestions}


# ── Version History & Diff ──


@doc_router.get("/{doc_id}/versions", response_model=list[DocumentResponse])
async def list_versions(
    doc_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await document_service.get_document(db, doc_id)
    if not doc or doc.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="文书不存在")
    versions = await document_service.list_versions(db, doc_id)
    return [DocumentResponse.model_validate(v) for v in versions]


@doc_router.get("/{doc_id}/versions/{target_id}/diff", response_model=VersionDiffResponse)
async def diff_versions(
    doc_id: uuid.UUID,
    target_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await document_service.get_document(db, doc_id)
    if not doc or doc.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="文书不存在")
    try:
        return await document_service.diff_versions(db, doc_id, target_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@doc_router.post("/{doc_id}/versions/{target_id}/rollback", response_model=DocumentResponse)
async def rollback_version(
    doc_id: uuid.UUID,
    target_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await document_service.get_document(db, doc_id)
    if not doc or doc.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="文书不存在")
    try:
        new_doc = await document_service.rollback_version(db, doc, target_id)
        return DocumentResponse.model_validate(new_doc)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ── Search-in-Context ──


@doc_router.post("/search-in-context")
async def search_in_context(
    query: str = Query(..., min_length=2),
    search_type: str = Query("law", pattern="^(law|case|both)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    results = {}
    if search_type in ("law", "both"):
        from app.services.knowledge_service import list_laws
        laws, _ = await list_laws(db, tenant_id=current_user.tenant_id, keyword=query, page=1, page_size=5)
        results["laws"] = [{"id": str(l.id), "title": l.title, "law_type": l.law_type} for l in laws]
    if search_type in ("case", "both"):
        from app.services.knowledge_service import list_precedent_cases
        cases, _ = await list_precedent_cases(db, tenant_id=current_user.tenant_id, keyword=query, page=1, page_size=5)
        results["cases"] = [{"id": str(c.id), "case_name": c.case_name, "case_type": c.case_type} for c in cases]
    return results


# ── Batch Generation ──


@doc_router.post("/batch-generate")
async def batch_generate(
    req: BatchGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tmpl = await document_service.get_template(db, req.template_id)
    if not tmpl:
        raise HTTPException(status_code=404, detail="模板不存在")
    created = []
    for variables in req.variable_sets:
        content = {"raw": tmpl.content_template, "variables": variables}
        doc = await document_service.create_document(
            db, current_user.tenant_id, current_user.id,
            {"template_id": str(req.template_id), "title": f"{tmpl.name} - 批量生成",
             "doc_type": tmpl.doc_type},
            content,
        )
        created.append(str(doc.id))
    return {"created_ids": created, "count": len(created)}


# ── Calculator Embedding ──


@doc_router.post("/{doc_id}/embed-calculation")
async def embed_calculation(
    doc_id: uuid.UUID,
    calc_type: str = Query(..., pattern="^(illegal_termination|overtime|annual_leave|work_injury)$"),
    params: dict = {},
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await document_service.get_document(db, doc_id)
    if not doc or doc.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="文书不存在")

    from app.services.calculator_service import calculate
    try:
        result = calculate(calc_type, params)
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Embed result into document content
    calc_section = f"\n\n--- 赔偿计算结果 ---\n计算类型: {calc_type}\n金额: ¥{result.result:,.2f}\n"
    for step in result.steps:
        calc_section += f"  {step}\n"

    existing = doc.content or {}
    raw = existing.get("raw", "")
    existing["raw"] = raw + calc_section
    doc.content = existing
    await db.flush()

    return {
        "result": result.result,
        "breakdown": result.breakdown,
        "basis": result.basis,
        "steps": result.steps,
    }
