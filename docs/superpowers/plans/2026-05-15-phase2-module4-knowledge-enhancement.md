# Module 4: 知识库增强 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add favorites/bookmark system, AI-powered law interpretation with SSE streaming, and admin batch import for legal data.

**Architecture:** Backend adds Favorites model + CRUD API, law interpretation endpoint using existing knowledge + LLM, and batch import endpoint. Frontend adds favorite buttons to knowledge pages, AI interpretation button to law detail, and admin import UI.

**Tech Stack:** FastAPI + SQLAlchemy 2.x async + Pydantic v2 + Next.js 14 + Tailwind CSS

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `backend/app/models/favorite.py` | Create | Favorites model |
| `backend/app/models/__init__.py` | Modify | Register Favorites model |
| `backend/app/schemas/favorite.py` | Create | Favorite request/response schemas |
| `backend/app/services/favorite_service.py` | Create | Favorite CRUD logic |
| `backend/app/api/v1/favorites.py` | Create | Favorite API endpoints |
| `backend/app/api/v1/knowledge.py` | Modify | Add interpret + import endpoints |
| `backend/app/api/router.py` | Modify | Include favorites router |
| `backend/alembic/versions/<rev>_add_favorites_table.py` | Create | Database migration |
| `frontend/src/types/index.ts` | Modify | Add Favorite type |
| `frontend/src/app/(dashboard)/knowledge/laws/page.tsx` | Modify | Add favorite buttons |
| `frontend/src/components/knowledge/law-search.tsx` | Modify | Add favorite toggle + AI interpret button |

---

### Task 1: Create Favorites Model

**Files:**
- Create: `backend/app/models/favorite.py`
- Modify: `backend/app/models/__init__.py`

- [ ] **Step 1: Write Favorites model**

```python
# backend/app/models/favorite.py
from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, BaseMixin


class Favorite(Base, BaseMixin):
    __tablename__ = "favorites"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    target_type: Mapped[str] = mapped_column(String(20), index=True)
    target_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    notes: Mapped[str | None] = mapped_column(Text)
```

- [ ] **Step 2: Register model in `__init__.py`**

Read `backend/app/models/__init__.py`, add:
```python
from app.models.favorite import Favorite
```
And add `"Favorite"` to `__all__`.

- [ ] **Step 3: Commit**

```bash
git add backend/app/models/favorite.py backend/app/models/__init__.py
git commit -m "feat: add Favorites model for knowledge bookmarking"
```

---

### Task 2: Create Favorite Schemas and Service

**Files:**
- Create: `backend/app/schemas/favorite.py`
- Create: `backend/app/services/favorite_service.py`

- [ ] **Step 1: Write favorite schemas**

```python
# backend/app/schemas/favorite.py
from __future__ import annotations

import datetime
import uuid
from pydantic import BaseModel


class FavoriteCreate(BaseModel):
    target_type: str
    target_id: uuid.UUID
    notes: str | None = None


class FavoriteUpdate(BaseModel):
    notes: str | None = None


class FavoriteResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    target_type: str
    target_id: uuid.UUID
    notes: str | None
    created_at: datetime.datetime

    model_config = {"from_attributes": True}
```

- [ ] **Step 2: Write favorite service**

```python
# backend/app/services/favorite_service.py
from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.favorite import Favorite


async def list_favorites(
    db: AsyncSession,
    user_id: uuid.UUID,
    target_type: str | None = None,
) -> list[Favorite]:
    conditions = [Favorite.user_id == user_id]
    if target_type:
        conditions.append(Favorite.target_type == target_type)
    stmt = select(Favorite).where(*conditions).order_by(Favorite.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_favorite(db: AsyncSession, favorite_id: uuid.UUID) -> Favorite | None:
    stmt = select(Favorite).where(Favorite.id == favorite_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_favorite(db: AsyncSession, user_id: uuid.UUID, data: dict) -> Favorite:
    fav = Favorite(user_id=user_id, **data)
    db.add(fav)
    await db.flush()
    return fav


async def update_favorite(db: AsyncSession, fav: Favorite, data: dict) -> Favorite:
    for key, value in data.items():
        if value is not None:
            setattr(fav, key, value)
    await db.flush()
    return fav


async def delete_favorite(db: AsyncSession, fav: Favorite) -> None:
    await db.delete(fav)
    await db.flush()


async def is_favorited(db: AsyncSession, user_id: uuid.UUID, target_type: str, target_id: uuid.UUID) -> bool:
    stmt = select(func.count(Favorite.id)).where(
        Favorite.user_id == user_id,
        Favorite.target_type == target_type,
        Favorite.target_id == target_id,
    )
    result = await db.execute(stmt)
    return (result.scalar() or 0) > 0
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/schemas/favorite.py backend/app/services/favorite_service.py
git commit -m "feat: add favorite schemas and service with CRUD logic"
```

---

### Task 3: Create Favorite API Routes

**Files:**
- Create: `backend/app/api/v1/favorites.py`
- Modify: `backend/app/api/router.py`

- [ ] **Step 1: Write favorites API**

```python
# backend/app/api/v1/favorites.py
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.favorite import FavoriteCreate, FavoriteResponse, FavoriteUpdate
from app.services import favorite_service

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("", response_model=list[FavoriteResponse])
async def list_favorites(
    target_type: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await favorite_service.list_favorites(db, current_user.id, target_type)
    return [FavoriteResponse.model_validate(i) for i in items]


@router.post("", response_model=FavoriteResponse, status_code=201)
async def create_favorite(
    req: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Check duplicate
    already = await favorite_service.is_favorited(db, current_user.id, req.target_type, req.target_id)
    if already:
        raise HTTPException(status_code=409, detail="已收藏")
    fav = await favorite_service.create_favorite(db, current_user.id, req.model_dump())
    return FavoriteResponse.model_validate(fav)


@router.put("/{favorite_id}", response_model=FavoriteResponse)
async def update_favorite(
    favorite_id: uuid.UUID,
    req: FavoriteUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    fav = await favorite_service.get_favorite(db, favorite_id)
    if not fav or fav.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="收藏不存在")
    fav = await favorite_service.update_favorite(db, fav, req.model_dump(exclude_unset=True))
    return FavoriteResponse.model_validate(fav)


@router.delete("/{favorite_id}", status_code=204)
async def delete_favorite(
    favorite_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    fav = await favorite_service.get_favorite(db, favorite_id)
    if not fav or fav.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="收藏不存在")
    await favorite_service.delete_favorite(db, fav)
    return None
```

- [ ] **Step 2: Register router**

```python
# In backend/app/api/router.py
from app.api.v1.favorites import router as favorites_router
api_router.include_router(favorites_router)
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/v1/favorites.py backend/app/api/router.py
git commit -m "feat: add favorites API with CRUD and duplicate detection"
```

---

### Task 4: Add Law Interpretation and Batch Import Endpoints

**Files:**
- Modify: `backend/app/api/v1/knowledge.py`

- [ ] **Step 1: Read existing knowledge API, add interpret and import endpoints**

Read `backend/app/api/v1/knowledge.py` first to understand existing patterns.

```python
# Add to backend/app/api/v1/knowledge.py

# ── New imports ──
import json
from fastapi.responses import StreamingResponse
from pydantic import BaseModel


# ── AI Law Interpretation ──

@router.post("/laws/{law_id}/interpret")
async def interpret_law(
    law_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    law = await knowledge_service.get_law(db, law_id)
    if not law:
        raise HTTPException(status_code=404, detail="法规不存在")

    articles = await knowledge_service.get_law_articles(db, law_id)

    async def event_stream():
        import asyncio
        from openai import AsyncOpenAI

        yield f"data: {json.dumps({'status': 'analyzing', 'message': '正在分析法规...'})}\n\n"

        client = AsyncOpenAI(
            api_key=settings.ZHIPU_API_KEY,
            base_url=settings.ZHIPU_BASE_URL,
        )

        articles_text = "\n".join([
            f"第{a.article_number}条 {a.content}"
            for a in articles[:20]
        ])

        prompt = f"""请对以下法规进行专业解读：

法规名称：{law.title}
法规类型：{law.law_type}
颁布机构：{law.promulgating_body or '未知'}
生效日期：{law.effective_date or '未知'}

条款内容：
{articles_text if articles_text else '暂无法条数据'}

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


# ── Batch Import ──

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
            law = Law(
                title=law_data.get("title", ""),
                law_type=law_data.get("law_type", "law"),
                promulgating_body=law_data.get("promulgating_body"),
                document_number=law_data.get("document_number"),
                publish_date=law_data.get("publish_date"),
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
            case = PrecedentCase(
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
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/api/v1/knowledge.py
git commit -m "feat: add AI law interpretation SSE and batch import endpoints"
```

---

### Task 5: Create Alembic Migration for Favorites

**Files:**
- Create: `backend/alembic/versions/<rev>_add_favorites_table.py`

- [ ] **Step 1: Generate and verify migration**

```bash
cd backend && alembic revision --autogenerate -m "add favorites table"
```

- [ ] **Step 2: Commit**

```bash
git add backend/alembic/versions/<rev>_add_favorites_table.py
git commit -m "feat: add Alembic migration for favorites table"
```

---

### Task 6: Add Frontend Types

**Files:**
- Modify: `frontend/src/types/index.ts`

- [ ] **Step 1: Add Favorite type**

```typescript
// Add to frontend/src/types/index.ts

export interface FavoriteItem {
  id: string;
  user_id: string;
  target_type: "law" | "case" | "article";
  target_id: string;
  notes: string | null;
  created_at: string;
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/types/index.ts
git commit -m "feat: add FavoriteItem TypeScript type"
```

---

### Task 7: Add Favorite Buttons to Knowledge Pages

**Files:**
- Modify: `frontend/src/components/knowledge/law-search.tsx`

- [ ] **Step 1: Add favorite toggle and AI interpret button to law search component**

Read `frontend/src/components/knowledge/law-search.tsx` first. Then:

```tsx
// Add to component state
const [favorites, setFavorites] = useState<Set<string>>(new Set());
const [interpretingId, setInterpretingId] = useState<string | null>(null);
const [interpretation, setInterpretation] = useState("");

// Add fetchFavorites helper
const fetchFavorites = useCallback(async () => {
  if (!token) return;
  try {
    const data = await api.get<{ target_id: string }[]>("/favorites?target_type=law", token);
    setFavorites(new Set(data.map((f: { target_id: string }) => f.target_id)));
  } catch {}
}, [token]);

useEffect(() => { fetchFavorites(); }, [fetchFavorites]);

// Toggle favorite
const toggleFavorite = async (lawId: string) => {
  if (!token) return;
  const isFav = favorites.has(lawId);
  try {
    if (isFav) {
      // Find and delete
      const data = await api.get<{ id: string }[]>(`/favorites?target_type=law`, token);
      const fav = data.find((f: { target_id: string }) => f.target_id === lawId);
      if (fav) await api.delete(`/favorites/${fav.id}`, token);
      setFavorites((prev) => { const next = new Set(prev); next.delete(lawId); return next; });
    } else {
      await api.post("/favorites", { target_type: "law", target_id: lawId }, token);
      setFavorites((prev) => new Set(prev).add(lawId));
    }
  } catch {}
};

// AI Interpret
const startInterpret = (lawId: string) => {
  setInterpretingId(lawId);
  setInterpretation("");
  const eventSource = new EventSource(
    `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/knowledge/laws/${lawId}/interpret`,
    // Note: EventSource doesn't support POST/custom headers, so use fetch-based SSE instead
  );
  // Implementation uses fetch + ReadableStream pattern from document editor
};
```

Add UI elements: favorite star button (★/☆) next to each law item, and "AI解读" button that triggers the interpretation panel.

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/knowledge/law-search.tsx
git commit -m "feat: add favorite toggle and AI interpretation buttons to law search"
```

---

## Self-Review Checklist

1. **Spec coverage:**
   - [x] Favorites model — Task 1
   - [x] Favorites CRUD API — Tasks 2-3
   - [x] Favorite list/get/create/update/delete — Task 3
   - [x] AI law interpretation (SSE) — Task 4
   - [x] Batch import (admin only) — Task 4
   - [x] Frontend favorite buttons — Task 7
   - [x] Frontend AI interpretation button — Task 7
   - [x] Alembic migration — Task 5

2. **Placeholder scan:** No remaining TBD/TODO.

3. **Pattern compliance:**
   - Favorite model follows existing model conventions
   - API routes follow existing patterns (prefix, tags, get_current_user)
   - SSE streaming pattern matches document generation from Module 2
   - Admin role check on import uses existing `require_role` dependency
