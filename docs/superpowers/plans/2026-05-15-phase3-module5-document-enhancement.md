# 文书增强 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans.

**Goal:** Enhance document center with version diff/rollback, law/case insertion, calculator integration, and batch generation.

**Architecture:** Extend existing document_service and documents API. No new DB tables — use existing Document.parent_id versioning.

**Tech Stack:** FastAPI, difflib, existing calculator_service, existing knowledge_service

---

### Task 1: Version History + Diff

**Files:**
- Modify: `backend/app/services/document_service.py`
- Modify: `backend/app/api/v1/documents.py`

Add to document_service:
```python
async def list_versions(db: AsyncSession, doc_id: uuid.UUID) -> list[Document]:
    doc = await get_document(db, doc_id)
    if not doc: return []
    # Find root document (follow parent_id chain)
    root_id = doc.id
    current = doc
    while current.parent_id:
        current = await get_document(db, current.parent_id)
        if not current: break
        root_id = current.id
    # Get all versions: root + all children pointing to root chain
    stmt = select(Document).where(
        or_(Document.id == root_id, Document.parent_id == root_id)
    ).order_by(Document.version)
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def diff_versions(db: AsyncSession, old_id: uuid.UUID, new_id: uuid.UUID) -> dict:
    import difflib
    old = await get_document(db, old_id)
    new = await get_document(db, new_id)
    if not old or not new: raise ValueError("版本不存在")
    old_text = old.content.get("raw", "") if old.content else ""
    new_text = new.content.get("raw", "") if new.content else ""
    diff = list(difflib.unified_diff(old_text.splitlines(), new_text.splitlines(), lineterm=""))
    diffs = []
    for i, line in enumerate(diff):
        if line.startswith("+") and not line.startswith("+++"):
            diffs.append({"type": "added", "line": i, "content": line[1:]})
        elif line.startswith("-") and not line.startswith("---"):
            diffs.append({"type": "removed", "line": i, "content": line[1:]})
    return {"old_version": old.version, "new_version": new.version, "diffs": diffs}

async def rollback_version(db: AsyncSession, doc: Document, target_id: uuid.UUID) -> Document:
    target = await get_document(db, target_id)
    if not target: raise ValueError("目标版本不存在")
    # Create new version with target content
    return await create_version(db, doc, {"content": target.content})
```

Add to documents API:
```python
@doc_router.get("/{doc_id}/versions")
async def list_versions(doc_id: uuid.UUID, ...):
    ...

@doc_router.get("/{doc_id}/versions/{target_id}/diff")
async def diff_versions(doc_id: uuid.UUID, target_id: uuid.UUID, ...):
    ...

@doc_router.post("/{doc_id}/versions/{target_id}/rollback")
async def rollback_version(doc_id: uuid.UUID, target_id: uuid.UUID, ...):
    ...
```

- [ ] Commit: `git commit -m "feat: add document version history, diff, and rollback"`

---

### Task 2: Law/Case Search-in-Context

**Files:**
- Modify: `backend/app/api/v1/documents.py`

Add endpoint:
```python
@doc_router.post("/search-in-context")
async def search_in_context(query: str = Query(..., min_length=2), search_type: str = Query("law", pattern="^(law|case|both)$"), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    results = {}
    if search_type in ("law", "both"):
        laws, _ = await list_laws(db, tenant_id=current_user.tenant_id, keyword=query, page=1, page_size=5)
        results["laws"] = [{"id": str(l.id), "title": l.title, "law_type": l.law_type} for l in laws]
    if search_type in ("case", "both"):
        cases, _ = await list_cases(db, tenant_id=current_user.tenant_id, keyword=query, page=1, page_size=5)
        results["cases"] = [{"id": str(c.id), "case_name": c.case_name, "case_type": c.case_type} for c in cases]
    return results
```

- [ ] Commit: `git commit -m "feat: add law/case search-in-context for document editor"`

---

### Task 3: Calculator Integration + Batch Generation

**Files:**
- Modify: `backend/app/api/v1/documents.py`

```python
@doc_router.post("/{doc_id}/embed-calculation")
async def embed_calculation(doc_id: uuid.UUID, calc_type: str = Query(...), params: dict = {}, ...):
    from app.services.calculator_service import calculate
    result = calculate(calc_type, params)
    return {"result": result.result, "basis": result.basis, "breakdown": result.breakdown}

class BatchGenerateRequest(BaseModel):
    template_id: uuid.UUID
    variable_sets: list[dict]

@doc_router.post("/batch-generate")
async def batch_generate(req: BatchGenerateRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tmpl = await document_service.get_template(db, req.template_id)
    if not tmpl: raise HTTPException(404, "模板不存在")
    created = []
    for variables in req.variable_sets[:20]:
        content = {"raw": tmpl.content_template, "variables": variables}
        doc = await document_service.create_document(db, current_user.tenant_id, current_user.id, {"template_id": str(req.template_id), "title": f"{tmpl.name} - 批量生成"}, content)
        created.append(str(doc.id))
    return {"created_ids": created, "count": len(created)}
```

- [ ] Commit: `git commit -m "feat: add calculator embedding and batch document generation"`

---

### Task 4: Tests

**Files:** Create: `backend/tests/test_document_enhance.py`

```python
import pytest
from unittest.mock import AsyncMock
from app.schemas.document import DocumentResponse

def test_diff_versions_basic():
    import difflib
    old = ["第一行", "第二行", "第三行"]
    new = ["第一行", "修改行", "第三行", "第四行"]
    diff = list(difflib.unified_diff(old, new, lineterm=""))
    assert any("修改行" in d for d in diff)

def test_batch_generate_request():
    from pydantic import BaseModel
    import uuid
    class BatchReq(BaseModel):
        template_id: uuid.UUID
        variable_sets: list[dict]
    req = BatchReq(template_id=uuid.uuid4(), variable_sets=[{"name": "张三"}])
    assert len(req.variable_sets) == 1
```

- [ ] Commit: `git commit -m "test: add document enhancement tests"`

---

### Task 5: Frontend Enhancements

**Files:**
- Modify: `frontend/src/app/(dashboard)/documents/[id]/page.tsx`
- Create: `frontend/src/components/document/version-panel.tsx`
- Create: `frontend/src/components/document/law-insert-dialog.tsx`

Add version history sidebar panel showing all versions with compare/rollback buttons.
Add law/case search dialog triggered from editor toolbar.
Add calculator button in toolbar that opens calculator modal and inserts result.

- [ ] Commit: `git commit -m "feat: add document version panel and law insert dialog to frontend"`
