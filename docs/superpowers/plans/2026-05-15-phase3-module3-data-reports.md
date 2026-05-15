# 数据报表/BI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans.

**Goal:** Build data reporting dashboard with case overview, trends, lawyer performance, and export capabilities.

**Architecture:** Aggregation queries from existing tables. No new DB tables. Recharts for frontend charts.

**Tech Stack:** FastAPI, SQLAlchemy aggregation, Recharts, openpyxl (export)

---

### Task 1: Schemas

**Files:** Create: `backend/app/schemas/report.py`

```python
from __future__ import annotations
from pydantic import BaseModel

class CaseTypeStat(BaseModel):
    type: str; count: int; amount: float

class CaseStatusStat(BaseModel):
    status: str; count: int

class CaseOverviewResponse(BaseModel):
    total: int
    by_type: list[CaseTypeStat]
    by_status: list[CaseStatusStat]
    avg_duration_days: float
    win_rate: float
    total_claim_amount: float

class TrendPeriod(BaseModel):
    period: str; total: int; by_type: dict[str, int]; avg_amount: float

class TrendsResponse(BaseModel):
    periods: list[TrendPeriod]

class LawyerStat(BaseModel):
    user_id: str; name: str; total_cases: int; win_rate: float; avg_satisfaction: float; total_claim_amount: float

class LawyerPerformanceResponse(BaseModel):
    lawyers: list[LawyerStat]; period_days: int

class ClientCaseSummary(BaseModel):
    id: str; title: str; status: str; claim_amount: float | None; created_at: str

class ClientReportResponse(BaseModel):
    client_name: str
    summary: dict
    cases: list[ClientCaseSummary]
```

---

### Task 2: Report Service

**Files:** Create: `backend/app/services/report_service.py`

```python
from __future__ import annotations
import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy import func, select, case, extract
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.case import Case
from app.models.feedback import ResponseFeedback

async def get_case_overview(db: AsyncSession, tenant_id: uuid.UUID, start_date: datetime | None = None, end_date: datetime | None = None) -> dict:
    conditions = [Case.tenant_id == tenant_id]
    if start_date: conditions.append(Case.created_at >= start_date)
    if end_date: conditions.append(Case.created_at <= end_date)
    # Total
    total = (await db.execute(select(func.count(Case.id)).where(*conditions))).scalar() or 0
    # By type
    type_rows = (await db.execute(select(Case.case_type.label("type"), func.count(Case.id).label("count"), func.coalesce(func.sum(Case.claim_amount), 0).label("amount")).where(*conditions).group_by(Case.case_type))).all()
    # By status
    status_rows = (await db.execute(select(Case.status.label("status"), func.count(Case.id).label("count")).where(*conditions).group_by(Case.status))).all()
    # Win rate (closed cases)
    closed = (await db.execute(select(func.count(Case.id)).where(*conditions, Case.status == "closed"))).scalar() or 0
    # Avg duration (closed cases)
    avg_dur = (await db.execute(select(func.avg(extract("day", Case.updated_at - Case.created_at))).where(*conditions, Case.status == "closed"))).scalar() or 0
    # Total amount
    total_amount = float((await db.execute(select(func.coalesce(func.sum(Case.claim_amount), 0)).where(*conditions))).scalar() or 0)
    return {
        "total": total,
        "by_type": [{"type": r.type, "count": r.count, "amount": float(r.amount)} for r in type_rows],
        "by_status": [{"status": r.status, "count": r.count} for r in status_rows],
        "avg_duration_days": round(float(avg_dur), 1),
        "win_rate": round(closed / total * 100, 1) if total > 0 else 0,
        "total_claim_amount": total_amount,
    }

async def get_trends(db: AsyncSession, tenant_id: uuid.UUID, granularity: str = "month", days: int = 180) -> dict:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    if granularity == "quarter":
        date_col = func.date_trunc("quarter", Case.created_at)
    else:
        date_col = func.date_trunc("month", Case.created_at)
    rows = (await db.execute(
        select(date_col.label("period"), func.count(Case.id).label("total"), func.coalesce(func.avg(Case.claim_amount), 0).label("avg_amount"))
        .where(Case.tenant_id == tenant_id, Case.created_at >= cutoff)
        .group_by("period").order_by("period")
    )).all()
    return {"periods": [{"period": str(r.period)[:10] if r.period else "", "total": r.total, "by_type": {}, "avg_amount": float(r.avg_amount)} for r in rows]}

async def get_lawyer_performance(db: AsyncSession, tenant_id: uuid.UUID, period_days: int = 90) -> dict:
    cutoff = datetime.now(timezone.utc) - timedelta(days=period_days)
    rows = (await db.execute(
        select(Case.lawyer_id.label("user_id"), func.count(Case.id).label("total_cases"), func.coalesce(func.sum(Case.claim_amount), 0).label("total_amount"))
        .where(Case.tenant_id == tenant_id, Case.created_at >= cutoff)
        .group_by(Case.lawyer_id).order_by(func.count(Case.id).desc())
    )).all()
    lawyers = []
    for r in rows:
        lawyers.append({"user_id": str(r.user_id), "name": "律师", "total_cases": r.total_cases, "win_rate": 0.0, "avg_satisfaction": 0.0, "total_claim_amount": float(r.total_amount)})
    return {"lawyers": lawyers, "period_days": period_days}
```

---

### Task 3: API Endpoints

**Files:** Create: `backend/app/api/v1/reports.py`, Modify: `backend/app/api/router.py`

```python
# backend/app/api/v1/reports.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models import User
from app.services import report_service

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/case-overview")
async def case_overview(days: int = Query(90, ge=1, le=365), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    from datetime import datetime, timedelta, timezone
    return await report_service.get_case_overview(db, current_user.tenant_id, datetime.now(timezone.utc) - timedelta(days=days))

@router.get("/trends")
async def trends(granularity: str = Query("month", pattern="^(month|quarter)$"), days: int = Query(180, ge=30, le=365), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await report_service.get_trends(db, current_user.tenant_id, granularity, days)

@router.get("/lawyer-performance")
async def lawyer_performance(period_days: int = Query(90, ge=30, le=365), current_user: User = Depends(require_role("platform_admin", "tenant_admin")), db: AsyncSession = Depends(get_db)):
    return await report_service.get_lawyer_performance(db, current_user.tenant_id, period_days)

@router.get("/export")
async def export_report(format: str = Query("xlsx", pattern="^(xlsx|pdf)$"), report_type: str = Query("case_overview"), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Placeholder — export requires openpyxl/reportlab
    raise NotImplementedError("导出功能待实现")
```

Register in router.py.

---

### Task 4: Tests

**Files:** Create: `backend/tests/test_reports.py`

```python
import pytest
from app.schemas.report import CaseOverviewResponse, TrendsResponse

def test_case_overview_schema():
    resp = CaseOverviewResponse(total=0, by_type=[], by_status=[], avg_duration_days=0, win_rate=0, total_claim_amount=0)
    assert resp.total == 0

def test_trends_schema():
    resp = TrendsResponse(periods=[])
    assert resp.periods == []
```

---

### Task 5: Frontend (Recharts)

**Files:**
- Install: `npm install recharts` in frontend/
- Create: `frontend/src/app/(dashboard)/reports/page.tsx`
- Create: `frontend/src/app/(dashboard)/reports/lawyer-performance/page.tsx`
- Modify: `layout.tsx` — add `{ href: "/reports", label: "数据报表", icon: "📊" }`

Overview page: PieChart for type distribution, BarChart for status distribution, LineChart for trends.
Lawyer performance page: ranking table with progress bars.

- [ ] Commit each step.
