# backend/app/api/v1/contracts.py
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.graphs.review_graph import build_review_graph
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User

router = APIRouter(prefix="/contracts", tags=["contracts"])

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB

# In-memory store for review reports (will be persisted in Module 5)
_review_reports: dict[str, dict] = {}


@router.post("/review")
async def review_contract(
    file: UploadFile | None = File(None),
    text: str | None = Form(None),
    concerns: str = Form(""),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    contract_text = ""

    if file:
        content = await file.read()
        if len(content) > MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=413, detail="文件大小不能超过10MB")
        try:
            contract_text = content.decode("utf-8")
        except UnicodeDecodeError:
            contract_text = content.decode("gbk", errors="replace")
    elif text:
        if len(text) > MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=413, detail="文本内容不能超过10MB")
        contract_text = text
    else:
        raise HTTPException(status_code=400, detail="请上传合同文件或粘贴合同文本")

    if len(contract_text) < 50:
        raise HTTPException(status_code=400, detail="合同内容过短，请提供完整的合同文本")

    graph = build_review_graph()
    result = await graph.ainvoke({
        "contract_text": contract_text,
        "user_concerns": concerns,
        "result": {},
        "error": "",
    })

    if result.get("error"):
        raise HTTPException(status_code=500, detail=f"合同审查失败: {result['error']}")

    report_id = str(uuid.uuid4())
    report = result["result"]
    report["id"] = report_id
    report["user_id"] = str(current_user.id)
    report["tenant_id"] = str(current_user.tenant_id)
    report["created_at"] = datetime.now(timezone.utc).isoformat()
    _review_reports[report_id] = report

    return report


@router.get("/{report_id}/report")
async def get_review_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
):
    report = _review_reports.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="审查报告不存在")
    if report.get("tenant_id") != str(current_user.tenant_id):
        raise HTTPException(status_code=403, detail="无权访问该报告")
    return report
