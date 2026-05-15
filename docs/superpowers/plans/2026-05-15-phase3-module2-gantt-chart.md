# 甘特图项目管理 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans.

**Goal:** Add Gantt chart visualization for case progress with drag support, preset templates, and overdue warnings.

**Architecture:** Store gantt data in existing `cases.gantt_data` JSONB. CSS-based Gantt chart (no external library). 4 node types with color coding.

**Tech Stack:** FastAPI, SQLAlchemy JSONB, Next.js, Tailwind CSS, pure CSS Gantt

---

### Task 1: Schemas

**Files:**
- Create: `backend/app/schemas/gantt.py`

```python
# backend/app/schemas/gantt.py
from __future__ import annotations
import datetime, uuid
from pydantic import BaseModel, Field

NODE_TYPES = ("deadline", "milestone", "task", "ai_assisted")
NODE_STATUSES = ("pending", "in_progress", "completed", "overdue")
DEP_TYPES = ("finish_to_start", "start_to_start", "finish_to_finish")

class GanttNode(BaseModel):
    id: str
    title: str
    type: str = Field(..., pattern="^(deadline|milestone|task|ai_assisted)$")
    start: str
    end: str
    assignee_id: str | None = None
    status: str = Field("pending", pattern="^(pending|in_progress|completed|overdue)$")
    progress: int = Field(0, ge=0, le=100)
    description: str | None = None

class GanttDependency(BaseModel):
    from_: str = Field(..., alias="from")
    to: str
    type: str = "finish_to_start"

class GanttData(BaseModel):
    nodes: list[GanttNode] = []
    dependencies: list[GanttDependency] = []

class GanttTemplateResponse(BaseModel):
    case_type: str
    gantt_data: GanttData

class GanttUpdateRequest(BaseModel):
    gantt_data: GanttData
```

- [ ] Commit: `git commit -m "feat: add Gantt chart schemas"`

---

### Task 2: Service

**Files:**
- Create: `backend/app/services/gantt_service.py`

```python
# backend/app/services/gantt_service.py
from __future__ import annotations
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.case import Case
from app.schemas.gantt import GanttData, GanttNode, GanttDependency

TEMPLATES = {
    "labor_arbitration": GanttData(nodes=[
        GanttNode(id="n1", title="咨询接待", type="task", start="today", end="+3d", status="pending", progress=0),
        GanttNode(id="n2", title="仲裁申请", type="milestone", start="+3d", end="+5d", status="pending", progress=0),
        GanttNode(id="n3", title="举证期限", type="deadline", start="+5d", end="+20d", status="pending", progress=0),
        GanttNode(id="n4", title="答辩状", type="task", start="+5d", end="+15d", status="pending", progress=0),
        GanttNode(id="n5", title="证据收集", type="ai_assisted", start="+5d", end="+18d", status="pending", progress=0),
        GanttNode(id="n6", title="开庭审理", type="milestone", start="+25d", end="+26d", status="pending", progress=0),
        GanttNode(id="n7", title="裁决", type="milestone", start="+35d", end="+45d", status="pending", progress=0),
        GanttNode(id="n8", title="执行", type="task", start="+45d", end="+60d", status="pending", progress=0),
    ], dependencies=[
        GanttDependency(**{"from": "n1", "to": "n2"}), GanttDependency(**{"from": "n2", "to": "n3"}),
        GanttDependency(**{"from": "n2", "to": "n4"}), GanttDependency(**{"from": "n3", "to": "n6"}),
        GanttDependency(**{"from": "n6", "to": "n7"}), GanttDependency(**{"from": "n7", "to": "n8"}),
    ]),
    "first_instance": GanttData(nodes=[
        GanttNode(id="n1", title="起诉准备", type="task", start="today", end="+5d"),
        GanttNode(id="n2", title="立案", type="milestone", start="+5d", end="+7d"),
        GanttNode(id="n3", title="举证", type="deadline", start="+7d", end="+25d"),
        GanttNode(id="n4", title="答辩状", type="task", start="+7d", end="+17d"),
        GanttNode(id="n5", title="证据交换", type="task", start="+20d", end="+22d"),
        GanttNode(id="n6", title="庭前准备", type="ai_assisted", start="+22d", end="+25d"),
        GanttNode(id="n7", title="一审开庭", type="milestone", start="+28d", end="+29d"),
        GanttNode(id="n8", title="法庭辩论", type="task", start="+29d", end="+30d"),
        GanttNode(id="n9", title="判决", type="milestone", start="+40d", end="+55d"),
        GanttNode(id="n10", title="执行申请", type="task", start="+55d", end="+70d"),
    ], dependencies=[
        GanttDependency(**{"from": "n1", "to": "n2"}), GanttDependency(**{"from": "n2", "to": "n3"}),
        GanttDependency(**{"from": "n2", "to": "n4"}), GanttDependency(**{"from": "n3", "to": "n5"}),
        GanttDependency(**{"from": "n5", "to": "n6"}), GanttDependency(**{"from": "n6", "to": "n7"}),
        GanttDependency(**{"from": "n7", "to": "n8"}), GanttDependency(**{"from": "n8", "to": "n9"}),
        GanttDependency(**{"from": "n9", "to": "n10"}),
    ]),
}

from datetime import date, timedelta
def _resolve_dates(nodes: list[GanttNode]) -> list[GanttNode]:
    today = date.today()
    for node in nodes:
        for field in ("start", "end"):
            val = getattr(node, field)
            if val == "today":
                setattr(node, field, today.isoformat())
            elif val.startswith("+"):
                days = int(val[1:-1])
                setattr(node, field, (today + timedelta(days=days)).isoformat())
    return nodes

async def get_gantt(db: AsyncSession, case_id: uuid.UUID) -> dict | None:
    from sqlalchemy import select
    stmt = select(Case.gantt_data).where(Case.id == case_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def update_gantt(db: AsyncSession, case_id: uuid.UUID, gantt_data: dict) -> None:
    from sqlalchemy import update
    await db.execute(update(Case).where(Case.id == case_id).values(gantt_data=gantt_data))
    await db.flush()

async def apply_template(db: AsyncSession, case: Case) -> dict:
    template = TEMPLATES.get(case.case_type)
    if not template:
        raise ValueError(f"无模板: {case.case_type}")
    resolved = _resolve_dates([GanttNode(**n.model_dump()) for n in template.nodes])
    data = GanttData(nodes=resolved, dependencies=template.dependencies)
    await update_gantt(db, case.id, data.model_dump())
    return data.model_dump()
```

- [ ] Commit: `git commit -m "feat: add Gantt chart service with templates"`

---

### Task 3: API

**Files:**
- Create: `backend/app/api/v1/gantt.py`
- Modify: `backend/app/api/router.py`

```python
# backend/app/api/v1/gantt.py
from __future__ import annotations
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.gantt import GanttData, GanttUpdateRequest
from app.services import gantt_service, case_service

router = APIRouter(prefix="/cases/{case_id}/gantt", tags=["gantt"])

@router.get("")
async def get_gantt(case_id: uuid.UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    case = await case_service.get_case(db, case_id, current_user.tenant_id)
    if not case: raise HTTPException(404, "案件不存在")
    return case.gantt_data or {"nodes": [], "dependencies": []}

@router.put("")
async def update_gantt(case_id: uuid.UUID, req: GanttUpdateRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    case = await case_service.get_case(db, case_id, current_user.tenant_id)
    if not case: raise HTTPException(404, "案件不存在")
    await gantt_service.update_gantt(db, case_id, req.gantt_data.model_dump())
    return req.gantt_data.model_dump()

@router.post("/apply-template")
async def apply_template(case_id: uuid.UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    case = await case_service.get_case(db, case_id, current_user.tenant_id)
    if not case: raise HTTPException(404, "案件不存在")
    try:
        return await gantt_service.apply_template(db, case)
    except ValueError as e:
        raise HTTPException(400, str(e))
```

Register in router.py. - [ ] Commit: `git commit -m "feat: add Gantt chart API endpoints"`

---

### Task 4: Tests

**Files:**
- Create: `backend/tests/test_gantt.py`

```python
# backend/tests/test_gantt.py
import pytest
from app.schemas.gantt import GanttNode, GanttData, GanttDependency

def test_gantt_node_validates_type():
    node = GanttNode(id="n1", title="test", type="milestone", start="2026-01-01", end="2026-01-05")
    assert node.type == "milestone"

def test_gantt_node_rejects_invalid_type():
    with pytest.raises(Exception): GanttNode(id="n1", title="test", type="invalid", start="2026-01-01", end="2026-01-05")

def test_gantt_data_model():
    data = GanttData(nodes=[GanttNode(id="n1", title="a", type="task", start="2026-01-01", end="2026-01-05")], dependencies=[GanttDependency(**{"from": "n1", "to": "n2"})])
    assert len(data.nodes) == 1

def test_gantt_template_exists():
    from app.services.gantt_service import TEMPLATES
    assert "labor_arbitration" in TEMPLATES
    assert "first_instance" in TEMPLATES
    assert len(TEMPLATES["labor_arbitration"].nodes) == 8
    assert len(TEMPLATES["first_instance"].nodes) == 10
```

- [ ] Commit: `git commit -m "test: add Gantt chart schema and template tests"`

---

### Task 5: Frontend

**Files:**
- Create: `frontend/src/app/(dashboard)/cases/[id]/gantt/page.tsx`
- Create: `frontend/src/components/gantt/gantt-chart.tsx`

CSS-based Gantt chart component: horizontal bars with color coding (red/blue/green/purple), today-line, drag to resize, tooltip for details. Page fetches gantt data, displays chart, supports apply-template button.

- [ ] Commit: `git commit -m "feat: add Gantt chart frontend page and component"`
