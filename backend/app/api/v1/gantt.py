from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.gantt import GanttUpdateRequest
from app.services import case_service, gantt_service

router = APIRouter(prefix="/cases/{case_id}/gantt", tags=["gantt"])


@router.get("")
async def get_gantt(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    case = await case_service.get_case(db, case_id, current_user.tenant_id)
    if not case:
        raise HTTPException(404, "案件不存在")
    return case.gantt_data or {"nodes": [], "dependencies": []}


@router.put("")
async def update_gantt(
    case_id: uuid.UUID,
    req: GanttUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    case = await case_service.get_case(db, case_id, current_user.tenant_id)
    if not case:
        raise HTTPException(404, "案件不存在")
    data = req.gantt_data.model_dump(by_alias=True)
    await gantt_service.update_gantt(db, case_id, data)
    return data


@router.post("/apply-template")
async def apply_template(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    case = await case_service.get_case(db, case_id, current_user.tenant_id)
    if not case:
        raise HTTPException(404, "案件不存在")
    try:
        return await gantt_service.apply_template(db, case)
    except ValueError as e:
        raise HTTPException(400, str(e))
