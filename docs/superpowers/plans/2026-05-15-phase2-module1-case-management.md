# Module 1: 案件管理 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver complete case CRUD with evidence upload, timeline management, and three frontend pages (list, detail, create).

**Architecture:** Backend adds Case/Evidence/CaseTimeline models + service + API routes following existing Phase 1 patterns (BaseMixin, async services, APIRouter). Frontend adds three pages under `(dashboard)/cases/` using the thin `lib/api-client.ts` wrapper and raw Tailwind CSS.

**Tech Stack:** FastAPI + SQLAlchemy 2.x async + Pydantic v2 + Next.js 14 App Router + Tailwind CSS

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `backend/app/models/case.py` | Create | Case, Evidence, CaseTimeline models |
| `backend/app/models/__init__.py` | Modify | Register new models |
| `backend/app/schemas/case.py` | Create | Request/response Pydantic schemas |
| `backend/app/services/case_service.py` | Create | Business logic (CRUD + filtering) |
| `backend/app/api/v1/cases.py` | Create | 13 API endpoints |
| `backend/app/api/router.py` | Modify | Include cases router |
| `backend/alembic/versions/<rev>_add_cases_tables.py` | Create | Database migration |
| `frontend/src/types/index.ts` | Modify | Add Case/Evidence/Timeline types |
| `frontend/src/app/(dashboard)/layout.tsx` | Modify | Add sidebar nav items |
| `frontend/src/app/(dashboard)/cases/page.tsx` | Create | Case list page |
| `frontend/src/app/(dashboard)/cases/[id]/page.tsx` | Create | Case detail page (multi-tab) |
| `frontend/src/app/(dashboard)/cases/new/page.tsx` | Create | Create case form |

---

### Task 1: Create Database Models

**Files:**
- Create: `backend/app/models/case.py`
- Modify: `backend/app/models/__init__.py`

- [ ] **Step 1: Write the Case, Evidence, and CaseTimeline models**

```python
# backend/app/models/case.py
from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import ARRAY, BigInteger, Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseMixin


class Case(Base, BaseMixin):
    __tablename__ = "cases"

    case_number: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    case_type: Mapped[str] = mapped_column(String(50), index=True)
    status: Mapped[str] = mapped_column(String(20), index=True, default="pending")
    plaintiff: Mapped[dict] = mapped_column(JSONB, default=dict)
    defendant: Mapped[dict] = mapped_column(JSONB, default=dict)
    claim_amount: Mapped[float | None] = mapped_column(Numeric(12, 2))
    dispute_focus: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    lawyer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    assistant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    gantt_data: Mapped[dict | None] = mapped_column(JSONB)
    ai_analysis: Mapped[dict | None] = mapped_column(JSONB)

    lawyer: Mapped["User"] = relationship("User", foreign_keys=[lawyer_id])
    assistant: Mapped["User | None"] = relationship("User", foreign_keys=[assistant_id])
    evidences: Mapped[list["Evidence"]] = relationship("Evidence", back_populates="case", cascade="all, delete-orphan")
    timelines: Mapped[list["CaseTimeline"]] = relationship("CaseTimeline", back_populates="case", cascade="all, delete-orphan")


class Evidence(Base, BaseMixin):
    __tablename__ = "evidences"

    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"), index=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    evidence_type: Mapped[str] = mapped_column(String(50))
    file_url: Mapped[str | None] = mapped_column(String(500))
    file_size: Mapped[int | None] = mapped_column(BigInteger)
    file_type: Mapped[str | None] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    case: Mapped["Case"] = relationship("Case", back_populates="evidences")


class CaseTimeline(Base, BaseMixin):
    __tablename__ = "case_timelines"

    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(20))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    event_date: Mapped[date] = mapped_column(Date)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    case: Mapped["Case"] = relationship("Case", back_populates="timelines")
```

- [ ] **Step 2: Register models in `__init__.py`**

Read `backend/app/models/__init__.py` first, then add the new imports.

```python
# Add these lines to backend/app/models/__init__.py
from app.models.case import Case, CaseTimeline, Evidence

# Add to __all__: "Case", "CaseTimeline", "Evidence"
```

The `__all__` list should include these three new names alongside the existing ones.

- [ ] **Step 3: Commit**

```bash
git add backend/app/models/case.py backend/app/models/__init__.py
git commit -m "feat: add Case, Evidence, CaseTimeline models for case management"
```

---

### Task 2: Create Pydantic Schemas

**Files:**
- Create: `backend/app/schemas/case.py`

- [ ] **Step 1: Write all request and response schemas**

```python
# backend/app/schemas/case.py
from __future__ import annotations

import datetime
import uuid
from pydantic import BaseModel, Field


# ── Plaintiff / Defendant sub-models ──

class PersonInfo(BaseModel):
    name: str = ""
    id_number: str = ""
    contact: str = ""


# ── Case schemas ──

class CaseCreate(BaseModel):
    title: str = Field(..., max_length=200)
    case_type: str
    plaintiff: PersonInfo = PersonInfo()
    defendant: PersonInfo = PersonInfo()
    claim_amount: float | None = None
    dispute_focus: list[str] | None = None
    assistant_id: uuid.UUID | None = None


class CaseUpdate(BaseModel):
    title: str | None = None
    case_type: str | None = None
    plaintiff: PersonInfo | None = None
    defendant: PersonInfo | None = None
    claim_amount: float | None = None
    dispute_focus: list[str] | None = None
    assistant_id: uuid.UUID | None = None


class CaseStatusUpdate(BaseModel):
    status: str


class CaseResponse(BaseModel):
    id: uuid.UUID
    case_number: str
    title: str
    case_type: str
    status: str
    plaintiff: dict
    defendant: dict
    claim_amount: float | None
    dispute_focus: list[str] | None
    lawyer_id: uuid.UUID
    assistant_id: uuid.UUID | None
    tenant_id: uuid.UUID
    gantt_data: dict | None
    ai_analysis: dict | None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


class CaseListResponse(BaseModel):
    items: list[CaseResponse]
    total: int
    page: int
    page_size: int


# ── Evidence schemas ──

class EvidenceCreate(BaseModel):
    title: str = Field(..., max_length=200)
    evidence_type: str
    description: str | None = None
    sort_order: int = 0


class EvidenceUpdate(BaseModel):
    title: str | None = None
    evidence_type: str | None = None
    description: str | None = None
    sort_order: int | None = None


class EvidenceResponse(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    tenant_id: uuid.UUID
    title: str
    evidence_type: str
    file_url: str | None
    file_size: int | None
    file_type: str | None
    description: str | None
    sort_order: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


# ── Timeline schemas ──

class TimelineCreate(BaseModel):
    event_type: str
    title: str = Field(..., max_length=200)
    description: str | None = None
    event_date: datetime.date


class TimelineUpdate(BaseModel):
    event_type: str | None = None
    title: str | None = None
    description: str | None = None
    event_date: datetime.date | None = None


class TimelineResponse(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    event_type: str
    title: str
    description: str | None
    event_date: datetime.date
    created_by: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/schemas/case.py
git commit -m "feat: add Pydantic schemas for case, evidence, and timeline"
```

---

### Task 3: Create Case Service

**Files:**
- Create: `backend/app/services/case_service.py`

- [ ] **Step 1: Write the case service with all CRUD + filtering logic**

```python
# backend/app/services/case_service.py
from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.case import Case, CaseTimeline, Evidence


# ── Case ──

async def generate_case_number(db: AsyncSession, tenant_id: uuid.UUID) -> str:
    """Generate sequential case number like LD-2026-0001."""
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
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/services/case_service.py
git commit -m "feat: add case service with CRUD, evidence, and timeline logic"
```

---

### Task 4: Create API Routes

**Files:**
- Create: `backend/app/api/v1/cases.py`
- Modify: `backend/app/api/router.py`

- [ ] **Step 1: Write the cases API router with all 13 endpoints**

```python
# backend/app/api/v1/cases.py
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
    case = await case_service.get_case(db, case_id)
    if not case or case.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="案件不存在")
    return CaseResponse.model_validate(case)


@router.put("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: uuid.UUID,
    req: CaseUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    case = await case_service.get_case(db, case_id)
    if not case or case.tenant_id != current_user.tenant_id:
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
    case = await case_service.get_case(db, case_id)
    if not case or case.tenant_id != current_user.tenant_id:
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
    case = await case_service.get_case(db, case_id)
    if not case or case.tenant_id != current_user.tenant_id:
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
    case = await case_service.get_case(db, case_id)
    if not case or case.tenant_id != current_user.tenant_id:
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
    case = await case_service.get_case(db, case_id)
    if not case or case.tenant_id != current_user.tenant_id:
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
    case = await case_service.get_case(db, case_id)
    if not case or case.tenant_id != current_user.tenant_id:
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
    await case_service.delete_timeline(db, timeline)
    return None
```

- [ ] **Step 2: Register the router in `backend/app/api/router.py`**

Read `backend/app/api/router.py` first.

```python
# Add this import in backend/app/api/router.py
from app.api.v1.cases import router as cases_router

# Add this line after the existing include_router calls
api_router.include_router(cases_router)
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/v1/cases.py backend/app/api/router.py
git commit -m "feat: add cases API routes with 13 endpoints for CRUD, evidence, and timeline"
```

---

### Task 5: Create Alembic Migration

**Files:**
- Create: `backend/alembic/versions/<rev>_add_cases_tables.py`

- [ ] **Step 1: Generate the migration**

```bash
cd backend && alembic revision --autogenerate -m "add cases tables"
```

Expected: Creates a new migration file in `backend/alembic/versions/`.

- [ ] **Step 2: Verify the migration file content**

Read the generated migration file. Verify it contains `create_table` for `cases`, `evidences`, and `case_timelines` with all columns from the model definitions.

- [ ] **Step 3: Commit**

```bash
git add backend/alembic/versions/<rev>_add_cases_tables.py
git commit -m "feat: add Alembic migration for cases, evidences, and case_timelines tables"
```

---

### Task 6: Add Frontend TypeScript Types

**Files:**
- Modify: `frontend/src/types/index.ts`

- [ ] **Step 1: Read the current types file, then add case-related types**

```typescript
// Add to frontend/src/types/index.ts

export interface PersonInfo {
  name: string;
  id_number: string;
  contact: string;
}

export interface CaseItem {
  id: string;
  case_number: string;
  title: string;
  case_type: string;
  status: string;
  plaintiff: PersonInfo;
  defendant: PersonInfo;
  claim_amount: number | null;
  dispute_focus: string[] | null;
  lawyer_id: string;
  assistant_id: string | null;
  tenant_id: string;
  gantt_data: Record<string, unknown> | null;
  ai_analysis: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface CaseListResponse {
  items: CaseItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface EvidenceItem {
  id: string;
  case_id: string;
  tenant_id: string;
  title: string;
  evidence_type: string;
  file_url: string | null;
  file_size: number | null;
  file_type: string | null;
  description: string | null;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface TimelineItem {
  id: string;
  case_id: string;
  event_type: string;
  title: string;
  description: string | null;
  event_date: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface CaseCreateRequest {
  title: string;
  case_type: string;
  plaintiff: PersonInfo;
  defendant: PersonInfo;
  claim_amount?: number;
  dispute_focus?: string[];
  assistant_id?: string;
}

export interface CaseUpdateRequest {
  title?: string;
  case_type?: string;
  plaintiff?: PersonInfo;
  defendant?: PersonInfo;
  claim_amount?: number;
  dispute_focus?: string[];
  assistant_id?: string;
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/types/index.ts
git commit -m "feat: add Case, Evidence, Timeline TypeScript types"
```

---

### Task 7: Add Constants (Case Types, Status Labels)

**Files:**
- Modify: `frontend/src/lib/constants.ts`

- [ ] **Step 1: Add case type and status constant maps**

```typescript
// Add to frontend/src/lib/constants.ts

export const CASE_TYPES: Record<string, string> = {
  labor_contract: "劳动合同",
  wage: "工资报酬",
  injury: "工伤",
  social_insurance: "社会保险",
  termination: "解除终止",
  discrimination: "歧视",
  other: "其他",
};

export const CASE_STATUSES: Record<string, string> = {
  pending: "待处理",
  in_progress: "处理中",
  filed: "已立案",
  hearing: "庭审中",
  mediating: "调解中",
  closed: "已结案",
  archived: "已归档",
  cancelled: "已撤销",
};

export const EVIDENCE_TYPES: Record<string, string> = {
  contract: "合同",
  chat_record: "聊天记录",
  photo: "照片",
  video: "视频",
  audio: "录音",
  document: "文档",
  other: "其他",
};
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/lib/constants.ts
git commit -m "feat: add case type, status, and evidence type constant maps"
```

---

### Task 8: Create Case List Page

**Files:**
- Create: `frontend/src/app/(dashboard)/cases/page.tsx`

- [ ] **Step 1: Write the case list page with search, filter, and pagination**

```tsx
"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/providers/auth-provider";
import { api } from "@/lib/api-client";
import { CASE_TYPES, CASE_STATUSES } from "@/lib/constants";
import type { CaseItem } from "@/types";

export default function CasesPage() {
  const { user, token } = useAuth();
  const router = useRouter();
  const [cases, setCases] = useState<CaseItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [search, setSearch] = useState("");
  const searchTimeout = useRef<ReturnType<typeof setTimeout>>();

  const fetchCases = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.set("page", String(page));
      params.set("page_size", "20");
      if (statusFilter) params.set("status", statusFilter);
      if (typeFilter) params.set("case_type", typeFilter);
      if (search) params.set("search", search);
      const data = await api.get<{ items: CaseItem[]; total: number }>(
        `/cases?${params.toString()}`,
        token
      );
      setCases(data.items);
      setTotal(data.total);
    } catch {
      // handled silently
    } finally {
      setLoading(false);
    }
  }, [token, page, statusFilter, typeFilter, search]);

  useEffect(() => {
    fetchCases();
  }, [fetchCases]);

  const handleSearch = (value: string) => {
    setSearch(value);
    clearTimeout(searchTimeout.current);
    searchTimeout.current = setTimeout(() => {
      setPage(1);
    }, 300);
  };

  const totalPages = Math.ceil(total / 20);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">案件管理</h1>
          <p className="text-sm text-muted-foreground mt-1">共 {total} 个案件</p>
        </div>
        <Link
          href="/cases/new"
          className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90"
        >
          + 新建案件
        </Link>
      </div>

      <div className="flex gap-3 flex-wrap">
        <input
          type="text"
          placeholder="搜索案件标题..."
          value={search}
          onChange={(e) => handleSearch(e.target.value)}
          className="rounded-md border px-3 py-2 text-sm bg-background w-64"
        />
        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
          className="rounded-md border px-3 py-2 text-sm bg-background"
        >
          <option value="">全部状态</option>
          {Object.entries(CASE_STATUSES).map(([k, v]) => (
            <option key={k} value={k}>{v}</option>
          ))}
        </select>
        <select
          value={typeFilter}
          onChange={(e) => { setTypeFilter(e.target.value); setPage(1); }}
          className="rounded-md border px-3 py-2 text-sm bg-background"
        >
          <option value="">全部类型</option>
          {Object.entries(CASE_TYPES).map(([k, v]) => (
            <option key={k} value={k}>{v}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <p className="text-center text-muted-foreground py-8">加载中...</p>
      ) : cases.length === 0 ? (
        <p className="text-center text-muted-foreground py-8">暂无案件</p>
      ) : (
        <>
          <div className="rounded-lg border overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-muted/50">
                <tr>
                  <th className="px-4 py-3 text-left font-medium">案号</th>
                  <th className="px-4 py-3 text-left font-medium">标题</th>
                  <th className="px-4 py-3 text-left font-medium">类型</th>
                  <th className="px-4 py-3 text-left font-medium">状态</th>
                  <th className="px-4 py-3 text-left font-medium">标的金额</th>
                  <th className="px-4 py-3 text-left font-medium">创建时间</th>
                </tr>
              </thead>
              <tbody>
                {cases.map((c) => (
                  <tr
                    key={c.id}
                    className="border-t hover:bg-muted/30 cursor-pointer"
                    onClick={() => router.push(`/cases/${c.id}`)}
                  >
                    <td className="px-4 py-3 font-mono text-xs">{c.case_number}</td>
                    <td className="px-4 py-3 font-medium">{c.title}</td>
                    <td className="px-4 py-3">{CASE_TYPES[c.case_type] || c.case_type}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                        c.status === "closed" || c.status === "archived"
                          ? "bg-green-100 text-green-700"
                          : c.status === "cancelled"
                          ? "bg-red-100 text-red-700"
                          : "bg-blue-100 text-blue-700"
                      }`}>
                        {CASE_STATUSES[c.status] || c.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {c.claim_amount != null ? `¥${c.claim_amount.toLocaleString()}` : "-"}
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">
                      {new Date(c.created_at).toLocaleDateString("zh-CN")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="rounded-md border px-3 py-1.5 text-sm disabled:opacity-50"
              >
                上一页
              </button>
              <span className="text-sm text-muted-foreground">
                第 {page} / {totalPages} 页
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="rounded-md border px-3 py-1.5 text-sm disabled:opacity-50"
              >
                下一页
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/app/\(dashboard\)/cases/page.tsx
git commit -m "feat: add case list page with search, filter, and pagination"
```

---

### Task 9: Create Case Detail Page

**Files:**
- Create: `frontend/src/app/(dashboard)/cases/[id]/page.tsx`

- [ ] **Step 1: Write the case detail page with multi-tab layout**

```tsx
"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import { api } from "@/lib/api-client";
import { CASE_TYPES, CASE_STATUSES, EVIDENCE_TYPES } from "@/lib/constants";
import type { CaseItem, EvidenceItem, TimelineItem } from "@/types";

const TABS = ["信息", "时间线", "证据"] as const;
type Tab = (typeof TABS)[number];

export default function CaseDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { token } = useAuth();
  const router = useRouter();
  const [caseData, setCaseData] = useState<CaseItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<Tab>("信息");

  // Evidence state
  const [evidences, setEvidences] = useState<EvidenceItem[]>([]);
  const [evLoading, setEvLoading] = useState(false);
  const [showEvidenceForm, setShowEvidenceForm] = useState(false);
  const [evTitle, setEvTitle] = useState("");
  const [evType, setEvType] = useState("document");
  const [evDesc, setEvDesc] = useState("");

  // Timeline state
  const [timelines, setTimelines] = useState<TimelineItem[]>([]);
  const [tlLoading, setTlLoading] = useState(false);
  const [showTimelineForm, setShowTimelineForm] = useState(false);
  const [tlType, setTlType] = useState("milestone");
  const [tlTitle, setTlTitle] = useState("");
  const [tlDesc, setTlDesc] = useState("");
  const [tlDate, setTlDate] = useState("");

  const fetchCase = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const data = await api.get<CaseItem>(`/cases/${id}`, token);
      setCaseData(data);
    } catch {
      router.push("/cases");
    } finally {
      setLoading(false);
    }
  }, [token, id, router]);

  const fetchEvidences = useCallback(async () => {
    if (!token) return;
    setEvLoading(true);
    try {
      const data = await api.get<EvidenceItem[]>(`/cases/${id}/evidences`, token);
      setEvidences(data);
    } finally {
      setEvLoading(false);
    }
  }, [token, id]);

  const fetchTimelines = useCallback(async () => {
    if (!token) return;
    setTlLoading(true);
    try {
      const data = await api.get<TimelineItem[]>(`/cases/${id}/timeline`, token);
      setTimelines(data);
    } finally {
      setTlLoading(false);
    }
  }, [token, id]);

  useEffect(() => { fetchCase(); }, [fetchCase]);
  useEffect(() => { if (tab === "证据") fetchEvidences(); }, [tab, fetchEvidences]);
  useEffect(() => { if (tab === "时间线") fetchTimelines(); }, [tab, fetchTimelines]);

  const addEvidence = async () => {
    if (!token || !evTitle.trim()) return;
    try {
      const params = new URLSearchParams();
      params.set("title", evTitle);
      params.set("evidence_type", evType);
      if (evDesc) params.set("description", evDesc);
      const data = await api.post<EvidenceItem>(`/cases/${id}/evidences?${params.toString()}`, {}, token);
      setEvidences((prev) => [...prev, data]);
      setShowEvidenceForm(false);
      setEvTitle("");
      setEvDesc("");
    } catch {}
  };

  const deleteEvidence = async (eid: string) => {
    if (!token) return;
    try {
      await api.delete(`/cases/${id}/evidences/${eid}`, token);
      setEvidences((prev) => prev.filter((e) => e.id !== eid));
    } catch {}
  };

  const addTimeline = async () => {
    if (!token || !tlTitle.trim() || !tlDate) return;
    try {
      const data = await api.post<TimelineItem>(`/cases/${id}/timeline`, {
        event_type: tlType, title: tlTitle, description: tlDesc || null, event_date: tlDate,
      }, token);
      setTimelines((prev) => [...prev, data]);
      setShowTimelineForm(false);
      setTlTitle("");
      setTlDesc("");
      setTlDate("");
    } catch {}
  };

  const deleteTimeline = async (tid: string) => {
    if (!token) return;
    try {
      await api.delete(`/cases/${id}/timeline/${tid}`, token);
      setTimelines((prev) => prev.filter((t) => t.id !== tid));
    } catch {}
  };

  if (loading) return <p className="p-6 text-center text-muted-foreground">加载中...</p>;
  if (!caseData) return <p className="p-6 text-center text-muted-foreground">案件不存在</p>;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <button onClick={() => router.push("/cases")} className="text-sm text-muted-foreground hover:text-foreground mb-1">
            ← 返回案件列表
          </button>
          <h1 className="text-2xl font-bold">{caseData.title}</h1>
          <p className="text-sm text-muted-foreground font-mono">{caseData.case_number}</p>
        </div>
        <span className={`rounded-full px-3 py-1 text-sm font-medium ${
          caseData.status === "closed" || caseData.status === "archived"
            ? "bg-green-100 text-green-700"
            : caseData.status === "cancelled"
            ? "bg-red-100 text-red-700"
            : "bg-blue-100 text-blue-700"
        }`}>
          {CASE_STATUSES[caseData.status] || caseData.status}
        </span>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              tab === t ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Tab: 信息 */}
      {tab === "信息" && (
        <div className="grid grid-cols-2 gap-6">
          <div className="rounded-lg border p-5 space-y-3">
            <h2 className="text-lg font-semibold">基本信息</h2>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div><span className="text-muted-foreground">案件类型：</span>{CASE_TYPES[caseData.case_type] || caseData.case_type}</div>
              <div><span className="text-muted-foreground">标的金额：</span>{caseData.claim_amount != null ? `¥${caseData.claim_amount.toLocaleString()}` : "未填写"}</div>
              <div><span className="text-muted-foreground">承办律师：</span>{caseData.lawyer_id}</div>
              <div><span className="text-muted-foreground">律师助理：</span>{caseData.assistant_id || "未指定"}</div>
              <div><span className="text-muted-foreground">创建时间：</span>{new Date(caseData.created_at).toLocaleString("zh-CN")}</div>
              <div><span className="text-muted-foreground">更新时间：</span>{new Date(caseData.updated_at).toLocaleString("zh-CN")}</div>
            </div>
            {caseData.dispute_focus && caseData.dispute_focus.length > 0 && (
              <div>
                <p className="text-sm text-muted-foreground mb-2">争议焦点</p>
                <div className="flex flex-wrap gap-2">
                  {caseData.dispute_focus.map((d, i) => (
                    <span key={i} className="rounded-full bg-accent px-2.5 py-0.5 text-xs">{d}</span>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="space-y-4">
            <div className="rounded-lg border p-5">
              <h2 className="text-lg font-semibold mb-3">原告信息</h2>
              <div className="space-y-1 text-sm">
                <p><span className="text-muted-foreground">姓名：</span>{caseData.plaintiff?.name || "-"}</p>
                <p><span className="text-muted-foreground">身份证号：</span>{caseData.plaintiff?.id_number || "-"}</p>
                <p><span className="text-muted-foreground">联系方式：</span>{caseData.plaintiff?.contact || "-"}</p>
              </div>
            </div>
            <div className="rounded-lg border p-5">
              <h2 className="text-lg font-semibold mb-3">被告信息</h2>
              <div className="space-y-1 text-sm">
                <p><span className="text-muted-foreground">名称：</span>{caseData.defendant?.name || "-"}</p>
                <p><span className="text-muted-foreground">统一社会信用代码：</span>{caseData.defendant?.id_number || "-"}</p>
                <p><span className="text-muted-foreground">联系方式：</span>{caseData.defendant?.contact || "-"}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab: 时间线 */}
      {tab === "时间线" && (
        <div className="space-y-4">
          <button
            onClick={() => setShowTimelineForm(!showTimelineForm)}
            className="text-sm rounded-md bg-primary px-3 py-1.5 text-primary-foreground hover:bg-primary/90"
          >
            + 添加事件
          </button>

          {showTimelineForm && (
            <div className="rounded-lg border p-4 space-y-3">
              <div className="flex gap-3">
                <select value={tlType} onChange={(e) => setTlType(e.target.value)} className="rounded-md border px-3 py-2 text-sm bg-background">
                  <option value="milestone">里程碑</option>
                  <option value="task">任务</option>
                  <option value="deadline">截止日期</option>
                  <option value="note">备注</option>
                </select>
                <input type="date" value={tlDate} onChange={(e) => setTlDate(e.target.value)} className="rounded-md border px-3 py-2 text-sm bg-background" />
              </div>
              <input type="text" placeholder="事件标题" value={tlTitle} onChange={(e) => setTlTitle(e.target.value)} className="w-full rounded-md border px-3 py-2 text-sm bg-background" />
              <textarea placeholder="事件描述（可选）" value={tlDesc} onChange={(e) => setTlDesc(e.target.value)} rows={2} className="w-full rounded-md border px-3 py-2 text-sm bg-background" />
              <button onClick={addTimeline} disabled={!tlTitle.trim() || !tlDate} className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50">
                保存
              </button>
            </div>
          )}

          {tlLoading ? (
            <p className="text-center text-muted-foreground py-4">加载中...</p>
          ) : timelines.length === 0 ? (
            <p className="text-center text-muted-foreground py-4">暂无时间线事件</p>
          ) : (
            <div className="space-y-3">
              {timelines.map((t) => (
                <div key={t.id} className="flex gap-4 rounded-lg border p-4">
                  <div className="text-sm text-muted-foreground whitespace-nowrap pt-0.5">
                    {new Date(t.event_date).toLocaleDateString("zh-CN")}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className={`inline-block rounded px-1.5 py-0.5 text-xs font-medium ${
                        t.event_type === "milestone" ? "bg-purple-100 text-purple-700" :
                        t.event_type === "deadline" ? "bg-red-100 text-red-700" :
                        "bg-blue-100 text-blue-700"
                      }`}>
                        {t.event_type === "milestone" ? "里程碑" : t.event_type === "task" ? "任务" : t.event_type === "deadline" ? "截止" : "备注"}
                      </span>
                      <span className="font-medium text-sm">{t.title}</span>
                    </div>
                    {t.description && <p className="text-sm text-muted-foreground mt-1">{t.description}</p>}
                  </div>
                  <button onClick={() => deleteTimeline(t.id)} className="text-sm text-destructive hover:underline shrink-0">
                    删除
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab: 证据 */}
      {tab === "证据" && (
        <div className="space-y-4">
          <button
            onClick={() => setShowEvidenceForm(!showEvidenceForm)}
            className="text-sm rounded-md bg-primary px-3 py-1.5 text-primary-foreground hover:bg-primary/90"
          >
            + 添加证据
          </button>

          {showEvidenceForm && (
            <div className="rounded-lg border p-4 space-y-3">
              <input type="text" placeholder="证据名称" value={evTitle} onChange={(e) => setEvTitle(e.target.value)} className="w-full rounded-md border px-3 py-2 text-sm bg-background" />
              <div className="flex gap-3">
                <select value={evType} onChange={(e) => setEvType(e.target.value)} className="rounded-md border px-3 py-2 text-sm bg-background">
                  {Object.entries(EVIDENCE_TYPES).map(([k, v]) => (
                    <option key={k} value={k}>{v}</option>
                  ))}
                </select>
              </div>
              <textarea placeholder="证据说明（可选）" value={evDesc} onChange={(e) => setEvDesc(e.target.value)} rows={2} className="w-full rounded-md border px-3 py-2 text-sm bg-background" />
              <button onClick={addEvidence} disabled={!evTitle.trim()} className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50">
                保存
              </button>
            </div>
          )}

          {evLoading ? (
            <p className="text-center text-muted-foreground py-4">加载中...</p>
          ) : evidences.length === 0 ? (
            <p className="text-center text-muted-foreground py-4">暂无证据</p>
          ) : (
            <div className="rounded-lg border overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="px-4 py-3 text-left font-medium">#</th>
                    <th className="px-4 py-3 text-left font-medium">名称</th>
                    <th className="px-4 py-3 text-left font-medium">类型</th>
                    <th className="px-4 py-3 text-left font-medium">说明</th>
                    <th className="px-4 py-3 text-left font-medium">大小</th>
                    <th className="px-4 py-3 text-left font-medium">操作</th>
                  </tr>
                </thead>
                <tbody>
                  {evidences.map((e, idx) => (
                    <tr key={e.id} className="border-t">
                      <td className="px-4 py-3 text-muted-foreground">{idx + 1}</td>
                      <td className="px-4 py-3 font-medium">{e.title}</td>
                      <td className="px-4 py-3">{EVIDENCE_TYPES[e.evidence_type] || e.evidence_type}</td>
                      <td className="px-4 py-3 text-muted-foreground">{e.description || "-"}</td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {e.file_size ? `${(e.file_size / 1024).toFixed(1)} KB` : "-"}
                      </td>
                      <td className="px-4 py-3">
                        <button onClick={() => deleteEvidence(e.id)} className="text-sm text-destructive hover:underline">
                          删除
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/app/\(dashboard\)/cases/\[id\]/page.tsx
git commit -m "feat: add case detail page with info, timeline, and evidence tabs"
```

---

### Task 10: Create Case Form Page

**Files:**
- Create: `frontend/src/app/(dashboard)/cases/new/page.tsx`

- [ ] **Step 1: Write the case creation form**

```tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import { api } from "@/lib/api-client";
import { CASE_TYPES } from "@/lib/constants";
import type { CaseItem } from "@/types";

export default function NewCasePage() {
  const { token } = useAuth();
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [caseType, setCaseType] = useState("labor_contract");
  const [pName, setPName] = useState("");
  const [pIdNumber, setPIdNumber] = useState("");
  const [pContact, setPContact] = useState("");
  const [dName, setDName] = useState("");
  const [dIdNumber, setDIdNumber] = useState("");
  const [dContact, setDContact] = useState("");
  const [claimAmount, setClaimAmount] = useState("");
  const [disputeFocus, setDisputeFocus] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) { setError("请输入案件标题"); return; }
    setError("");
    setLoading(true);
    try {
      const data = await api.post<CaseItem>("/cases", {
        title: title.trim(),
        case_type: caseType,
        plaintiff: { name: pName.trim(), id_number: pIdNumber.trim(), contact: pContact.trim() },
        defendant: { name: dName.trim(), id_number: dIdNumber.trim(), contact: dContact.trim() },
        claim_amount: claimAmount ? parseFloat(claimAmount) : undefined,
        dispute_focus: disputeFocus ? disputeFocus.split(",").map((s) => s.trim()).filter(Boolean) : undefined,
      }, token!);
      router.push(`/cases/${data.id}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "创建失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl">
      <button onClick={() => router.push("/cases")} className="text-sm text-muted-foreground hover:text-foreground mb-4">
        ← 返回案件列表
      </button>
      <h1 className="text-2xl font-bold mb-6">新建案件</h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        {error && <p className="text-sm text-destructive bg-destructive/10 rounded-md px-4 py-2">{error}</p>}

        {/* 基本信息 */}
        <div className="rounded-lg border p-5 space-y-4">
          <h2 className="text-lg font-semibold">基本信息</h2>
          <div>
            <label className="text-sm font-medium">案件标题 *</label>
            <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1" placeholder="如：张某某与XX公司劳动争议案" />
          </div>
          <div>
            <label className="text-sm font-medium">案件类型</label>
            <select value={caseType} onChange={(e) => setCaseType(e.target.value)} className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1">
              {Object.entries(CASE_TYPES).map(([k, v]) => (
                <option key={k} value={k}>{v}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-sm font-medium">标的金额</label>
            <input type="number" value={claimAmount} onChange={(e) => setClaimAmount(e.target.value)} className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1" placeholder="单位：元" />
          </div>
          <div>
            <label className="text-sm font-medium">争议焦点</label>
            <input type="text" value={disputeFocus} onChange={(e) => setDisputeFocus(e.target.value)} className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1" placeholder="多个用逗号分隔，如：加班费,经济补偿金" />
          </div>
        </div>

        {/* 原告信息 */}
        <div className="rounded-lg border p-5 space-y-4">
          <h2 className="text-lg font-semibold">原告信息</h2>
          <div>
            <label className="text-sm font-medium">姓名</label>
            <input type="text" value={pName} onChange={(e) => setPName(e.target.value)} className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1" />
          </div>
          <div>
            <label className="text-sm font-medium">身份证号</label>
            <input type="text" value={pIdNumber} onChange={(e) => setPIdNumber(e.target.value)} className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1" />
          </div>
          <div>
            <label className="text-sm font-medium">联系方式</label>
            <input type="text" value={pContact} onChange={(e) => setPContact(e.target.value)} className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1" />
          </div>
        </div>

        {/* 被告信息 */}
        <div className="rounded-lg border p-5 space-y-4">
          <h2 className="text-lg font-semibold">被告信息</h2>
          <div>
            <label className="text-sm font-medium">名称（单位/个人）</label>
            <input type="text" value={dName} onChange={(e) => setDName(e.target.value)} className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1" />
          </div>
          <div>
            <label className="text-sm font-medium">统一社会信用代码/身份证号</label>
            <input type="text" value={dIdNumber} onChange={(e) => setDIdNumber(e.target.value)} className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1" />
          </div>
          <div>
            <label className="text-sm font-medium">联系方式</label>
            <input type="text" value={dContact} onChange={(e) => setDContact(e.target.value)} className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1" />
          </div>
        </div>

        <div className="flex gap-3">
          <button type="submit" disabled={loading} className="rounded-md bg-primary px-6 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50">
            {loading ? "创建中..." : "创建案件"}
          </button>
          <button type="button" onClick={() => router.push("/cases")} className="rounded-md border px-6 py-2 text-sm hover:bg-accent">
            取消
          </button>
        </div>
      </form>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/app/\(dashboard\)/cases/new/page.tsx
git commit -m "feat: add case creation form page"
```

---

### Task 11: Update Sidebar Navigation

**Files:**
- Modify: `frontend/src/app/(dashboard)/layout.tsx`

- [ ] **Step 1: Add "案件管理" to the navItems array**

Read `frontend/src/app/(dashboard)/layout.tsx` first. Locate the `navItems` array and add the new entry after the chat item:

```typescript
const navItems = [
  { href: "/dashboard", label: "概览", icon: "📊" },
  { href: "/chat", label: "智能咨询", icon: "💬" },
  { href: "/cases", label: "案件管理", icon: "📋" },  // ← new
  { href: "/calculator", label: "赔偿计算", icon: "🧮" },
  { href: "/knowledge", label: "知识库", icon: "📚" },
  { href: "/token-usage", label: "Token 监控", icon: "📈" },
  { href: "/settings", label: "设置", icon: "⚙️" },
];
```

- [ ] **Step 2: Verify the layout file still compiles**

```bash
cd frontend && npx tsc --noEmit
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/app/\(dashboard\)/layout.tsx
git commit -m "feat: add cases nav item to sidebar"
```

---

## Self-Review Checklist

1. **Spec coverage:**
   - [x] Case CRUD — Tasks 3, 4 (list/get/create/update/status)
   - [x] Evidence CRUD — Tasks 3, 4 (list/create/update/delete)
   - [x] Timeline CRUD — Tasks 3, 4 (list/create/update/delete)
   - [x] Case list page with search/filter/pagination — Task 8
   - [x] Case detail page with multi-tab — Task 9
   - [x] Create case form — Task 10
   - [x] Sidebar nav update — Task 11
   - [x] 8-case status, 7-case types — Models (Task 1) + Constants (Task 7)
   - [x] Auto-generated case number — Task 3 (generate_case_number)
   - [x] Alembic migration — Task 5

2. **Placeholder scan:** No TBD/TODO/fill-in-later. All code is explicit.

3. **Type consistency:** CaseCreate/CaseUpdate/CaseResponse schema names match between service, route, and frontend usage. Evidence/EvidenceItem, Timeline/TimelineItem types are consistent.

4. **Pattern compliance:**
   - Backend: BaseMixin, async services, APIRouter prefix, get_current_user dependency, model_validate conversion
   - Frontend: "use client" pages, api.get/post from lib/api-client, Tailwind CSS tokens (rounded-lg, border, bg-muted/50, text-muted-foreground), useState for form state
