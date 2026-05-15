from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.case import (
    CaseCreate,
    CaseListResponse,
    CaseResponse,
    CaseStatusUpdate,
    CaseUpdate,
    EvidenceCreate,
    EvidenceResponse,
    EvidenceUpdate,
    TimelineCreate,
    TimelineResponse,
    TimelineUpdate,
)
from app.ai.graphs.analysis_graph import build_analysis_graph
from app.services import case_service

router = APIRouter(prefix="/cases", tags=["cases"])


# ── Case CRUD ──

@router.get("", response_model=CaseListResponse)
async def list_cases(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    case_type: str | None = None,
    lawyer_id: uuid.UUID | None = None,
    search: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await case_service.list_cases(
        db, current_user.tenant_id, page, page_size, status, case_type, lawyer_id, search
    )
    return CaseListResponse(
        items=[CaseResponse.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=CaseResponse, status_code=201)
async def create_case(
    req: CaseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data = req.model_dump(exclude_unset=True)
    plaintiff = data.pop("plaintiff", None)
    defendant = data.pop("defendant", None)
    if plaintiff:
        data["plaintiff"] = plaintiff if isinstance(plaintiff, dict) else plaintiff.model_dump()
    if defendant:
        data["defendant"] = defendant if isinstance(defendant, dict) else defendant.model_dump()
    case = await case_service.create_case(db, current_user.tenant_id, current_user.id, data)
    return CaseResponse.model_validate(case)


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    case = await case_service.get_case(db, case_id, current_user.tenant_id)
    if not case:
        raise HTTPException(status_code=404, detail="案件不存在")
    return CaseResponse.model_validate(case)


@router.put("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: uuid.UUID,
    req: CaseUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    case = await case_service.get_case(db, case_id, current_user.tenant_id)
    if not case:
        raise HTTPException(status_code=404, detail="案件不存在")
    data = req.model_dump(exclude_unset=True)
    if "plaintiff" in data and data["plaintiff"] and not isinstance(data["plaintiff"], dict):
        data["plaintiff"] = data["plaintiff"].model_dump()
    if "defendant" in data and data["defendant"] and not isinstance(data["defendant"], dict):
        data["defendant"] = data["defendant"].model_dump()
    case = await case_service.update_case(db, case, data)
    return CaseResponse.model_validate(case)


@router.patch("/{case_id}/status", response_model=CaseResponse)
async def update_case_status(
    case_id: uuid.UUID,
    req: CaseStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    case = await case_service.get_case(db, case_id, current_user.tenant_id)
    if not case:
        raise HTTPException(status_code=404, detail="案件不存在")
    case = await case_service.update_case_status(db, case, req.status)
    return CaseResponse.model_validate(case)


# ── Evidence ──

@router.get("/{case_id}/evidences", response_model=list[EvidenceResponse])
async def list_evidences(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    case = await case_service.get_case(db, case_id, current_user.tenant_id)
    if not case:
        raise HTTPException(status_code=404, detail="案件不存在")
    items = await case_service.list_evidences(db, case_id)
    return [EvidenceResponse.model_validate(i) for i in items]


@router.post("/{case_id}/evidences", response_model=EvidenceResponse, status_code=201)
async def upload_evidence(
    case_id: uuid.UUID,
    title: str = Query(...),
    evidence_type: str = Query(...),
    description: str | None = Query(None),
    sort_order: int = Query(0),
    file: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    case = await case_service.get_case(db, case_id, current_user.tenant_id)
    if not case:
        raise HTTPException(status_code=404, detail="案件不存在")
    data = {"title": title, "evidence_type": evidence_type, "description": description, "sort_order": sort_order}
    file_url = None
    file_size = None
    file_type = None
    if file:
        file_url = f"/uploads/{case_id}/{file.filename}"
        file_size = file.size
        file_type = file.content_type
    evidence = await case_service.create_evidence(db, case_id, current_user.tenant_id, data, file_url, file_size, file_type)
    return EvidenceResponse.model_validate(evidence)


@router.put("/{case_id}/evidences/{evidence_id}", response_model=EvidenceResponse)
async def update_evidence(
    case_id: uuid.UUID,
    evidence_id: uuid.UUID,
    req: EvidenceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    evidence = await case_service.get_evidence(db, evidence_id)
    if not evidence or evidence.case_id != case_id or evidence.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="证据不存在")
    evidence = await case_service.update_evidence(db, evidence, req.model_dump(exclude_unset=True))
    return EvidenceResponse.model_validate(evidence)


@router.delete("/{case_id}/evidences/{evidence_id}", status_code=204)
async def delete_evidence(
    case_id: uuid.UUID,
    evidence_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    evidence = await case_service.get_evidence(db, evidence_id)
    if not evidence or evidence.case_id != case_id or evidence.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="证据不存在")
    await case_service.delete_evidence(db, evidence)
    return None


# ── Timeline ──

@router.get("/{case_id}/timeline", response_model=list[TimelineResponse])
async def list_timelines(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    case = await case_service.get_case(db, case_id, current_user.tenant_id)
    if not case:
        raise HTTPException(status_code=404, detail="案件不存在")
    items = await case_service.list_timelines(db, case_id)
    return [TimelineResponse.model_validate(i) for i in items]


@router.post("/{case_id}/timeline", response_model=TimelineResponse, status_code=201)
async def create_timeline(
    case_id: uuid.UUID,
    req: TimelineCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    case = await case_service.get_case(db, case_id, current_user.tenant_id)
    if not case:
        raise HTTPException(status_code=404, detail="案件不存在")
    timeline = await case_service.create_timeline(db, case_id, current_user.id, req.model_dump())
    return TimelineResponse.model_validate(timeline)


@router.put("/{case_id}/timeline/{timeline_id}", response_model=TimelineResponse)
async def update_timeline(
    case_id: uuid.UUID,
    timeline_id: uuid.UUID,
    req: TimelineUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    timeline = await case_service.get_timeline(db, timeline_id)
    if not timeline or timeline.case_id != case_id:
        raise HTTPException(status_code=404, detail="时间线事件不存在")
    case = await case_service.get_case(db, case_id, current_user.tenant_id)
    if not case:
        raise HTTPException(status_code=404, detail="案件不存在")
    timeline = await case_service.update_timeline(db, timeline, req.model_dump(exclude_unset=True))
    return TimelineResponse.model_validate(timeline)


@router.delete("/{case_id}/timeline/{timeline_id}", status_code=204)
async def delete_timeline(
    case_id: uuid.UUID,
    timeline_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    timeline = await case_service.get_timeline(db, timeline_id)
    if not timeline or timeline.case_id != case_id:
        raise HTTPException(status_code=404, detail="时间线事件不存在")
    case = await case_service.get_case(db, case_id, current_user.tenant_id)
    if not case:
        raise HTTPException(status_code=404, detail="案件不存在")
    await case_service.delete_timeline(db, timeline)
    return None


# ── AI Analysis ──

@router.post("/{case_id}/analyze")
async def analyze_case(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    case = await case_service.get_case(db, case_id, current_user.tenant_id)
    if not case:
        raise HTTPException(status_code=404, detail="案件不存在")

    evidences = await case_service.list_evidences(db, case_id)
    timelines = await case_service.list_timelines(db, case_id)

    case_data = {
        "title": case.title,
        "case_type": case.case_type,
        "plaintiff": case.plaintiff,
        "defendant": case.defendant,
        "claim_amount": float(case.claim_amount) if case.claim_amount else None,
        "dispute_focus": case.dispute_focus,
        "evidences": [{"title": e.title, "type": e.evidence_type, "description": e.description} for e in evidences],
        "timeline": [{"date": str(t.event_date), "type": t.event_type, "title": t.title, "description": t.description} for t in timelines],
    }

    graph = build_analysis_graph()
    result = await graph.ainvoke({"case_data": case_data, "result": {}, "error": ""})

    if result.get("error"):
        raise HTTPException(status_code=500, detail=f"AI分析失败: {result['error']}")

    await case_service.update_case(db, case, {"ai_analysis": result["result"]})

    return {"case_id": str(case_id), "analysis": result["result"]}
