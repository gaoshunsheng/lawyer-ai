# 咨询增强 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans.

**Goal:** Enhance existing chat/consultation with follow-up questions, file attachments, conversation export, and case linking.

**Architecture:** Modify existing consult_graph.py + chat API. Add file_parser service. New DB columns on chat_sessions/chat_messages.

**Tech Stack:** FastAPI, python-docx, PyPDF2, LangGraph, SSE

---

### Task 1: Follow-up Questions

**Files:**
- Modify: `backend/app/ai/prompts/legal_prompts.py`
- Modify: `backend/app/ai/graphs/consult_graph.py`
- Create: migration for chat_sessions.follow_up_count + chat_messages.is_follow_up

Add `FOLLOW_UP_PROMPT` to legal_prompts.py:
```python
FOLLOW_UP_PROMPT = """根据以下对话，检查是否缺少关键信息。劳动法律咨询需要的信息包括：当事人身份(员工/用人单位)、工作时间、工资标准、争议类型。

当前对话：
{conversation}

如果缺少关键信息，生成一个追问问题。返回JSON：{{"needs_follow_up": true/false, "question": "追问问题", "missing_info": ["缺少的信息"]}}"""
```

Modify `generate_answer` in consult_graph.py: after generating answer, if follow_up_count < 3, call follow-up check.

Migration: add `follow_up_count INTEGER DEFAULT 0` to chat_sessions, `is_follow_up BOOLEAN DEFAULT FALSE` to chat_messages.

- [ ] Commit: `git commit -m "feat: add follow-up question logic to consultation"`

---

### Task 2: File Attachments

**Files:**
- Create: `backend/app/services/file_parser.py`
- Modify: `backend/app/api/v1/chat.py`

```python
# backend/app/services/file_parser.py
from __future__ import annotations
async def parse_file(content: bytes, filename: str, content_type: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext == "pdf":
        from io import BytesIO
        from PyPDF2 import PdfReader
        reader = PdfReader(BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages[:20])
    elif ext in ("doc", "docx"):
        from io import BytesIO
        from docx import Document
        doc = Document(BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs[:100])
    elif content_type and content_type.startswith("text/"):
        return content.decode("utf-8", errors="replace")
    return ""
```

Add to chat API: `POST /chat/sessions/{id}/attachments` — upload file, parse text, inject into next message context.

Migration: add `attachments JSONB` to chat_messages (if not exists).

- [ ] Commit: `git commit -m "feat: add file attachment parsing for chat"`

---

### Task 3: Conversation Export

**Files:**
- Modify: `backend/app/api/v1/chat.py`

Add `POST /chat/sessions/{id}/export?format=docx|pdf`:
- Fetch all messages for session
- Generate Word doc with python-docx: title = "咨询记录", each message as paragraph with role prefix
- Return as StreamingResponse with appropriate Content-Type

```python
@router.post("/sessions/{session_id}/export")
async def export_session(session_id: uuid.UUID, format: str = Query("docx", pattern="^(docx|pdf)$"), ...):
    # Fetch messages, build document, return file
```

- [ ] Commit: `git commit -m "feat: add conversation export to Word/PDF"`

---

### Task 4: Case Linking

**Files:**
- Modify: `backend/app/api/v1/chat.py`
- Create: migration for chat_sessions.case_id

Add endpoints:
- `POST /chat/sessions/{id}/link-case` — body: {case_id: uuid}, sets chat_sessions.case_id
- `DELETE /chat/sessions/{id}/link-case` — clears case_id

When linked, inject case context (title, type, plaintiff, defendant) into consult_graph's system prompt.

Migration: add `case_id UUID FK cases.id NULL` to chat_sessions.

- [ ] Commit: `git commit -m "feat: add case linking to chat sessions"`

---

### Task 5: Tests

**Files:** Create: `backend/tests/test_consultation_enhance.py`

```python
import pytest
from app.services.file_parser import parse_file

@pytest.mark.asyncio
async def test_parse_text_file():
    result = await parse_file(b"hello world", "test.txt", "text/plain")
    assert "hello" in result

@pytest.mark.asyncio
async def test_parse_pdf_empty():
    result = await parse_file(b"", "test.pdf", "application/pdf")
    assert result == ""

@pytest.mark.asyncio
async def test_parse_unsupported():
    result = await parse_file(b"\x00\x01", "test.xyz", "application/octet-stream")
    assert result == ""
```

- [ ] Commit: `git commit -m "test: add consultation enhancement tests"`
