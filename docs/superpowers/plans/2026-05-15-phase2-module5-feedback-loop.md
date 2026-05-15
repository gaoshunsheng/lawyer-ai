# Module 5: 数据反馈飞轮 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the data feedback loop with in-chat rating component, aggregated feedback dashboard with satisfaction trends, and negative-rate alerting.

**Architecture:** Phase 1 already has `response_feedbacks` table and `/api/v1/feedback` POST endpoint. Module 5 adds aggregated stats + trends API endpoints, a feedback rating component integrated into the chat interface, and an admin feedback dashboard page with charts.

**Tech Stack:** FastAPI + SQLAlchemy 2.x async + Next.js 14 + Tailwind CSS + Recharts (charts)

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `backend/app/api/v1/feedback.py` | Modify | Add stats + trends endpoints |
| `backend/app/services/feedback_service.py` | Create | Aggregation logic |
| `frontend/src/components/chat/feedback-form.tsx` | Modify | Enhance with 3-dimension star ratings |
| `frontend/src/app/(dashboard)/feedback/page.tsx` | Create | Admin feedback dashboard |
| `frontend/src/app/(dashboard)/layout.tsx` | Modify | Add feedback nav item (admin only) |

---

### Task 1: Create Feedback Aggregation Service

**Files:**
- Create: `backend/app/services/feedback_service.py`

- [ ] **Step 1: Write feedback aggregation service**

```python
# backend/app/services/feedback_service.py
from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta

from sqlalchemy import func, select, case, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.feedback import ResponseFeedback


async def get_feedback_stats(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    days: int = 30,
) -> dict:
    """Aggregate feedback stats for the last N days."""
    cutoff = datetime.now() - timedelta(days=days)

    base_condition = [
        ResponseFeedback.tenant_id == tenant_id,
        ResponseFeedback.created_at >= cutoff,
    ]

    # Total count
    count_stmt = select(func.count(ResponseFeedback.id)).where(*base_condition)
    total = (await db.execute(count_stmt)).scalar() or 0

    if total == 0:
        return {
            "total": 0,
            "positive_rate": 0,
            "negative_rate": 0,
            "avg_law_accuracy": 0,
            "avg_analysis_depth": 0,
            "avg_practical_value": 0,
        }

    # Positive rate
    pos_stmt = select(func.count(ResponseFeedback.id)).where(
        *base_condition,
        ResponseFeedback.overall_positive == True,
    )
    positive_count = (await db.execute(pos_stmt)).scalar() or 0

    # Average scores
    avg_stmt = select(
        func.avg(ResponseFeedback.law_accuracy_score).label("avg_law"),
        func.avg(ResponseFeedback.analysis_depth_score).label("avg_depth"),
        func.avg(ResponseFeedback.practical_value_score).label("avg_value"),
    ).where(*base_condition)
    avg_result = (await db.execute(avg_stmt)).one()

    return {
        "total": total,
        "positive_rate": round(positive_count / total * 100, 1),
        "negative_rate": round((total - positive_count) / total * 100, 1),
        "avg_law_accuracy": round(avg_result.avg_law or 0, 2),
        "avg_analysis_depth": round(avg_result.avg_depth or 0, 2),
        "avg_practical_value": round(avg_result.avg_value or 0, 2),
    }


async def get_feedback_trends(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    days: int = 30,
    granularity: str = "day",
) -> list[dict]:
    """Get daily/weekly/monthly satisfaction trends."""
    cutoff = datetime.now() - timedelta(days=days)

    if granularity == "month":
        date_col = func.date_trunc("month", ResponseFeedback.created_at)
    elif granularity == "week":
        date_col = func.date_trunc("week", ResponseFeedback.created_at)
    else:
        date_col = func.date_trunc("day", ResponseFeedback.created_at)

    stmt = (
        select(
            date_col.label("period"),
            func.count(ResponseFeedback.id).label("total"),
            func.sum(case((ResponseFeedback.overall_positive == True, 1), else_=0)).label("positive"),
        )
        .where(
            ResponseFeedback.tenant_id == tenant_id,
            ResponseFeedback.created_at >= cutoff,
        )
        .group_by("period")
        .order_by("period")
    )

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "period": str(row.period),
            "total": row.total,
            "positive": row.positive or 0,
            "negative": row.total - (row.positive or 0),
            "satisfaction_rate": round((row.positive or 0) / row.total * 100, 1) if row.total > 0 else 0,
        }
        for row in rows
    ]
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/services/feedback_service.py
git commit -m "feat: add feedback aggregation service with stats and trends"
```

---

### Task 2: Add Stats + Trends API Endpoints

**Files:**
- Modify: `backend/app/api/v1/feedback.py`

- [ ] **Step 1: Read existing feedback API, add stats and trends endpoints**

Read `backend/app/api/v1/feedback.py` first. Then add:

```python
# Add imports
from app.services import feedback_service as fb_service

# Add endpoints after existing POST handler

@router.get("/stats")
async def get_feedback_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_role("platform_admin", "tenant_admin")),
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated feedback statistics (admin only)."""
    stats = await fb_service.get_feedback_stats(db, current_user.tenant_id, days)
    return stats


@router.get("/trends")
async def get_feedback_trends(
    days: int = Query(30, ge=1, le=365),
    granularity: str = Query("day", pattern="^(day|week|month)$"),
    current_user: User = Depends(require_role("platform_admin", "tenant_admin")),
    db: AsyncSession = Depends(get_db),
):
    """Get satisfaction trends over time (admin only)."""
    trends = await fb_service.get_feedback_trends(db, current_user.tenant_id, days, granularity)
    return trends
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/api/v1/feedback.py
git commit -m "feat: add feedback stats and trends API endpoints (admin only)"
```

---

### Task 3: Enhance Feedback Form Component

**Files:**
- Modify: `frontend/src/components/chat/feedback-form.tsx`

- [ ] **Step 1: Read existing feedback form, enhance with 3-dimension star ratings**

Read `frontend/src/components/chat/feedback-form.tsx` first. Enhance the component:

```tsx
// The existing component likely has basic positive/negative toggle.
// Enhance with 3 dimension star ratings:

// Add dimension state (may already exist):
const [scores, setScores] = useState({ law: 0, depth: 0, value: 0 });

// Star rating renderer inline:
const StarRating = ({ label, value, onChange }: { label: string; value: number; onChange: (v: number) => void }) => (
  <div className="flex items-center gap-2">
    <span className="text-xs text-muted-foreground w-20">{label}</span>
    <div className="flex gap-0.5">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          onClick={() => onChange(star)}
          className={`text-lg ${star <= value ? "text-yellow-400" : "text-gray-300"} hover:text-yellow-400 transition-colors`}
        >
          ★
        </button>
      ))}
    </div>
  </div>
);

// In JSX, after overall positive/negative buttons:
{isPositive !== null && (
  <div className="space-y-2 py-3 border-t">
    <p className="text-xs text-muted-foreground">请对本次回复进行评价（可选）</p>
    <StarRating label="法条准确性" value={scores.law} onChange={(v) => setScores((s) => ({ ...s, law: v }))} />
    <StarRating label="分析深度" value={scores.depth} onChange={(v) => setScores((s) => ({ ...s, depth: v }))} />
    <StarRating label="实用价值" value={scores.value} onChange={(v) => setScores((s) => ({ ...s, value: v }))} />
    <textarea
      value={textFeedback}
      onChange={(e) => setTextFeedback(e.target.value)}
      maxLength={500}
      rows={3}
      placeholder="补充你的评价（最多500字）..."
      className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-2"
    />
    <div className="flex justify-between items-center">
      <span className="text-xs text-muted-foreground">{textFeedback.length}/500</span>
      <button
        onClick={handleSubmit}
        disabled={submitted}
        className="rounded-md bg-primary px-4 py-1.5 text-xs text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
      >
        {submitted ? "已提交" : "提交评价"}
      </button>
    </div>
  </div>
)}
```

The enhancement keeps existing overall thumbs-up/down, then reveals star ratings and text feedback after the user picks positive/negative.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/chat/feedback-form.tsx
git commit -m "feat: enhance feedback form with 3-dimension star ratings and 500-char text"
```

---

### Task 4: Create Admin Feedback Dashboard Page

**Files:**
- Create: `frontend/src/app/(dashboard)/feedback/page.tsx`

- [ ] **Step 1: Write the feedback dashboard page with stats cards and trends**

```tsx
"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/providers/auth-provider";
import { api } from "@/lib/api-client";

interface FeedbackStats {
  total: number;
  positive_rate: number;
  negative_rate: number;
  avg_law_accuracy: number;
  avg_analysis_depth: number;
  avg_practical_value: number;
}

interface TrendPoint {
  period: string;
  total: number;
  positive: number;
  negative: number;
  satisfaction_rate: number;
}

export default function FeedbackPage() {
  const { user, token } = useAuth();
  const [stats, setStats] = useState<FeedbackStats | null>(null);
  const [trends, setTrends] = useState<TrendPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);
  const [granularity, setGranularity] = useState("day");

  const isAdmin = user?.role === "platform_admin" || user?.role === "tenant_admin";

  const fetchData = useCallback(async () => {
    if (!token || !isAdmin) return;
    setLoading(true);
    try {
      const [statsRes, trendsRes] = await Promise.all([
        api.get<FeedbackStats>(`/feedback/stats?days=${days}`, token),
        api.get<TrendPoint[]>(`/feedback/trends?days=${days}&granularity=${granularity}`, token),
      ]);
      setStats(statsRes);
      setTrends(trendsRes);
    } finally {
      setLoading(false);
    }
  }, [token, isAdmin, days, granularity]);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (!isAdmin) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold">反馈看板</h1>
        <p className="text-muted-foreground mt-4">仅管理员可查看反馈统计数据。</p>
      </div>
    );
  }

  // Simple bar chart using CSS (no external chart library needed)
  const maxSatisfaction = Math.max(...trends.map((t) => t.satisfaction_rate), 1);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">反馈看板</h1>
          <p className="text-sm text-muted-foreground mt-1">
            {days === 1 ? "今日" : days === 7 ? "本周" : days === 30 ? "本月" : `近${days}天`}数据
          </p>
        </div>
        <div className="flex gap-2">
          <select value={days} onChange={(e) => setDays(Number(e.target.value))}
            className="rounded-md border px-3 py-2 text-sm bg-background">
            <option value={1}>今日</option>
            <option value={7}>近7天</option>
            <option value={30}>近30天</option>
            <option value={90}>近90天</option>
          </select>
          <select value={granularity} onChange={(e) => setGranularity(e.target.value)}
            className="rounded-md border px-3 py-2 text-sm bg-background">
            <option value="day">按日</option>
            <option value="week">按周</option>
            <option value="month">按月</option>
          </select>
        </div>
      </div>

      {loading ? (
        <p className="text-center text-muted-foreground py-8">加载中...</p>
      ) : (
        <>
          {/* Stat cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="rounded-lg border p-4">
              <p className="text-sm text-muted-foreground">总评价数</p>
              <p className="text-2xl font-bold mt-1">{stats?.total || 0}</p>
            </div>
            <div className="rounded-lg border p-4">
              <p className="text-sm text-muted-foreground">好评率</p>
              <p className={`text-2xl font-bold mt-1 ${(stats?.positive_rate || 0) >= 85 ? "text-green-600" : "text-yellow-600"}`}>
                {stats?.positive_rate || 0}%
              </p>
            </div>
            <div className="rounded-lg border p-4">
              <p className="text-sm text-muted-foreground">差评率</p>
              <p className={`text-2xl font-bold mt-1 ${(stats?.negative_rate || 0) > 15 ? "text-red-600" : "text-green-600"}`}>
                {stats?.negative_rate || 0}%
                {(stats?.negative_rate || 0) > 15 && (
                  <span className="text-xs font-normal text-red-500 ml-2">⚠ 预警</span>
                )}
              </p>
            </div>
            <div className="rounded-lg border p-4">
              <p className="text-sm text-muted-foreground">综合均分</p>
              <p className="text-2xl font-bold mt-1">
                {stats ? ((stats.avg_law_accuracy + stats.avg_analysis_depth + stats.avg_practical_value) / 3).toFixed(1) : "-"}
              </p>
            </div>
          </div>

          {/* Dimension scores */}
          {stats && (
            <div className="grid grid-cols-3 gap-4">
              <div className="rounded-lg border p-4 text-center">
                <p className="text-sm text-muted-foreground">法条准确性</p>
                <p className="text-xl font-bold mt-1">{stats.avg_law_accuracy.toFixed(1)}</p>
                <div className="flex justify-center gap-0.5 mt-1">
                  {[1, 2, 3, 4, 5].map((s) => (
                    <span key={s} className={`text-sm ${s <= Math.round(stats.avg_law_accuracy) ? "text-yellow-400" : "text-gray-300"}`}>★</span>
                  ))}
                </div>
              </div>
              <div className="rounded-lg border p-4 text-center">
                <p className="text-sm text-muted-foreground">分析深度</p>
                <p className="text-xl font-bold mt-1">{stats.avg_analysis_depth.toFixed(1)}</p>
                <div className="flex justify-center gap-0.5 mt-1">
                  {[1, 2, 3, 4, 5].map((s) => (
                    <span key={s} className={`text-sm ${s <= Math.round(stats.avg_analysis_depth) ? "text-yellow-400" : "text-gray-300"}`}>★</span>
                  ))}
                </div>
              </div>
              <div className="rounded-lg border p-4 text-center">
                <p className="text-sm text-muted-foreground">实用价值</p>
                <p className="text-xl font-bold mt-1">{stats.avg_practical_value.toFixed(1)}</p>
                <div className="flex justify-center gap-0.5 mt-1">
                  {[1, 2, 3, 4, 5].map((s) => (
                    <span key={s} className={`text-sm ${s <= Math.round(stats.avg_practical_value) ? "text-yellow-400" : "text-gray-300"}`}>★</span>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Satisfaction trends */}
          <div className="rounded-lg border p-5">
            <h2 className="text-lg font-semibold mb-4">满意度趋势</h2>
            {trends.length === 0 ? (
              <p className="text-center text-muted-foreground py-8">暂无趋势数据</p>
            ) : (
              <div className="space-y-2">
                {trends.map((t) => (
                  <div key={t.period} className="flex items-center gap-3">
                    <span className="text-xs text-muted-foreground w-24 shrink-0">
                      {granularity === "month"
                        ? t.period.slice(0, 7)
                        : t.period.slice(0, 10)}
                    </span>
                    <div className="flex-1 bg-muted rounded-full h-6 relative overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${t.satisfaction_rate >= 85 ? "bg-green-500" : t.satisfaction_rate >= 70 ? "bg-yellow-500" : "bg-red-500"}`}
                        style={{ width: `${Math.max(t.satisfaction_rate, 2)}%` }}
                      />
                    </div>
                    <span className={`text-xs font-medium w-14 text-right ${t.satisfaction_rate >= 85 ? "text-green-600" : t.satisfaction_rate >= 70 ? "text-yellow-600" : "text-red-600"}`}>
                      {t.satisfaction_rate}%
                    </span>
                    <span className="text-xs text-muted-foreground w-16 text-right">
                      {t.total}条
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Alert section */}
          {(stats?.negative_rate || 0) > 15 && (
            <div className="rounded-lg border border-red-200 bg-red-50 p-4">
              <h3 className="font-semibold text-red-700 flex items-center gap-2">
                <span>⚠</span> 差评率预警
              </h3>
              <p className="text-sm text-red-600 mt-1">
                当前差评率为 {stats?.negative_rate}%，超过15%阈值。建议检查近期的AI回复质量，并查看具体差评内容以定位问题。
              </p>
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
git add frontend/src/app/\(dashboard\)/feedback/page.tsx
git commit -m "feat: add admin feedback dashboard with stats, trends, and alerting"
```

---

### Task 5: Update Sidebar Navigation (Admin-Only Nav Items)

**Files:**
- Modify: `frontend/src/app/(dashboard)/layout.tsx`

- [ ] **Step 1: Add "反馈看板" nav item for admin users only**

Read `frontend/src/app/(dashboard)/layout.tsx` first.

Modify the nav rendering to conditionally show the feedback link:

```tsx
// Inside the component, after useAuth() / usePathname():
const { user } = useAuth();
const isAdmin = user?.role === "platform_admin" || user?.role === "tenant_admin";

// In the navItems rendering, add after the main items and before token-usage:
{isAdmin && (
  <Link
    key="/feedback"
    href="/feedback"
    className={`flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors ${
      pathname === "/feedback" ? "bg-accent text-accent-foreground font-medium" : "text-muted-foreground hover:bg-accent/50"
    }`}
  >
    <span>📊</span>
    <span>反馈看板</span>
  </Link>
)}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/app/\(dashboard\)/layout.tsx
git commit -m "feat: add feedback dashboard nav item for admin users"
```

---

## Self-Review Checklist

1. **Spec coverage:**
   - [x] Feedback stats API (aggregated) — Tasks 1-2
   - [x] Feedback trends API — Tasks 1-2
   - [x] Enhanced feedback form (3 dimensions + text) — Task 3
   - [x] 5-star rating per dimension — Task 3
   - [x] 500-char text feedback — Task 3
   - [x] Feedback dashboard page (stats cards + trends + alerting) — Task 4
   - [x] Negative rate >15% alert — Task 4
   - [x] Admin-only sidebar nav item — Task 5
   - [x] Day/week/month granularity selector — Task 4

2. **Placeholder scan:** No TBD/TODO.

3. **Pattern compliance:**
   - Service follows existing async function pattern
   - API routes with admin role guard
   - Frontend page uses "use client" + api.get pattern
   - CSS bar chart avoids external chart library dependency
   - Sidebar conditional rendering matches existing auth patterns

4. **Integration note:** The existing `POST /api/v1/feedback` endpoint from Phase 1 already writes to `response_feedbacks`. The new stats/trends endpoints read from the same table — no migration needed for the feedback table itself.
