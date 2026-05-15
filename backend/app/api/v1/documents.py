# backend/app/api/v1/documents.py
from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.document import (
    DocumentCreate,
    DocumentGenerateRequest,
    DocumentListResponse,
    DocumentResponse,
    DocumentUpdate,
    TemplateResponse,
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
    template_id = data.pop("template_id", None)
    data["template_id"] = template_id

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
            yield f"data: {json.dumps({'status': 'complete', 'content': {'html': f'<pre>{text}</pre>'}})}\n\n"
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
    return PlainTextResponse(
        content=text,
        headers={"Content-Disposition": f"attachment; filename={doc.title}.txt"},
    )


# ── AI Smart Suggest ──

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
