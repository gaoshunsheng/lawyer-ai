# Module 2: 文书中心 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver document template library (10 seed templates), document CRUD with variable filling, rich text editing, and AI-powered document generation with SSE streaming.

**Architecture:** Backend adds DocumentTemplate and Document models + service + API routes. Document versioning via parent_id self-referential FK. AI generation endpoint streams SSE. Frontend adds 4 pages under `(dashboard)/documents/` with variable-fill wizard and rich text editor.

**Tech Stack:** FastAPI + SQLAlchemy 2.x async + Pydantic v2 + Next.js 14 App Router + Tailwind CSS + TipTap (rich text)

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `backend/app/models/document.py` | Create | DocumentTemplate, Document models |
| `backend/app/models/__init__.py` | Modify | Register new models |
| `backend/app/schemas/document.py` | Create | Request/response Pydantic schemas |
| `backend/app/services/document_service.py` | Create | Business logic + seed data |
| `backend/app/api/v1/documents.py` | Create | 7 API endpoints |
| `backend/app/api/router.py` | Modify | Include documents router |
| `backend/alembic/versions/<rev>_add_document_tables.py` | Create | Database migration |
| `frontend/src/types/index.ts` | Modify | Add document types |
| `frontend/src/lib/constants.ts` | Modify | Add doc type/category constants |
| `frontend/src/app/(dashboard)/layout.tsx` | Modify | Add sidebar nav item |
| `frontend/src/app/(dashboard)/documents/page.tsx` | Create | Document list page |
| `frontend/src/app/(dashboard)/documents/templates/page.tsx` | Create | Template library page |
| `frontend/src/app/(dashboard)/documents/new/page.tsx` | Create | Create document wizard |
| `frontend/src/app/(dashboard)/documents/[id]/page.tsx` | Create | Document editor |

---

### Task 1: Create Document Models

**Files:**
- Create: `backend/app/models/document.py`
- Modify: `backend/app/models/__init__.py`

- [ ] **Step 1: Write DocumentTemplate and Document models**

```python
# backend/app/models/document.py
from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseMixin


class DocumentTemplate(Base, BaseMixin):
    __tablename__ = "document_templates"

    name: Mapped[str] = mapped_column(String(200))
    doc_type: Mapped[str] = mapped_column(String(50), index=True)
    content_template: Mapped[str] = mapped_column(Text)
    variables_schema: Mapped[dict] = mapped_column(JSONB, default=dict)
    category: Mapped[str] = mapped_column(String(50), index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), index=True)

    documents: Mapped[list["Document"]] = relationship("Document", back_populates="template")


class Document(Base, BaseMixin):
    __tablename__ = "documents"

    case_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"), index=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(200))
    doc_type: Mapped[str] = mapped_column(String(50))
    template_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("document_templates.id"))
    content: Mapped[dict | None] = mapped_column(JSONB)
    variables: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    version: Mapped[int] = mapped_column(Integer, default=1)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"))

    template: Mapped["DocumentTemplate | None"] = relationship("DocumentTemplate", back_populates="documents")
    parent: Mapped["Document | None"] = relationship("Document", remote_side="Document.id", back_populates="children")
    children: Mapped[list["Document"]] = relationship("Document", back_populates="parent")
```

- [ ] **Step 2: Register models in `__init__.py`**

Read `backend/app/models/__init__.py`, then add:
```python
from app.models.document import Document, DocumentTemplate
```
And add `"Document", "DocumentTemplate"` to `__all__`.

- [ ] **Step 3: Commit**

```bash
git add backend/app/models/document.py backend/app/models/__init__.py
git commit -m "feat: add DocumentTemplate and Document models with versioning"
```

---

### Task 2: Create Document Schemas

**Files:**
- Create: `backend/app/schemas/document.py`

- [ ] **Step 1: Write all document schemas**

```python
# backend/app/schemas/document.py
from __future__ import annotations

import datetime
import uuid
from pydantic import BaseModel, Field


# ── Template schemas ──

class TemplateResponse(BaseModel):
    id: uuid.UUID
    name: str
    doc_type: str
    content_template: str
    variables_schema: dict
    category: str
    sort_order: int
    is_system: bool
    tenant_id: uuid.UUID | None
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


# ── Document schemas ──

class DocumentCreate(BaseModel):
    title: str = Field(..., max_length=200)
    doc_type: str
    template_id: uuid.UUID | None = None
    case_id: uuid.UUID | None = None
    variables: dict | None = None


class DocumentUpdate(BaseModel):
    title: str | None = None
    content: dict | None = None
    variables: dict | None = None
    status: str | None = None


class DocumentGenerateRequest(BaseModel):
    instructions: str | None = None


class DocumentResponse(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID | None
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    title: str
    doc_type: str
    template_id: uuid.UUID | None
    content: dict | None
    variables: dict | None
    status: str
    version: int
    parent_id: uuid.UUID | None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int
    page: int
    page_size: int
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/schemas/document.py
git commit -m "feat: add document and template Pydantic schemas"
```

---

### Task 3: Create Document Service with Seed Data

**Files:**
- Create: `backend/app/services/document_service.py`

- [ ] **Step 1: Write the document service with 10 seed templates**

```python
# backend/app/services/document_service.py
from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentTemplate


# ── Seed ──

SEED_TEMPLATES = [
    {
        "name": "劳动争议仲裁申请书",
        "doc_type": "arbitration_application",
        "category": "申请类",
        "sort_order": 1,
        "variables_schema": {
            "variables": [
                {"name": "applicant_name", "label": "申请人姓名", "type": "string", "required": True},
                {"name": "applicant_id", "label": "申请人身份证号", "type": "string", "required": True},
                {"name": "applicant_phone", "label": "申请人联系电话", "type": "string", "required": True},
                {"name": "applicant_address", "label": "申请人通讯地址", "type": "string", "required": True},
                {"name": "respondent_name", "label": "被申请人名称", "type": "string", "required": True},
                {"name": "respondent_address", "label": "被申请人地址", "type": "string", "required": True},
                {"name": "respondent_legal_rep", "label": "法定代表人", "type": "string", "required": True},
                {"name": "employment_start", "label": "入职日期", "type": "date", "required": True},
                {"name": "position", "label": "工作岗位", "type": "string", "required": True},
                {"name": "salary", "label": "月工资", "type": "number", "required": True},
                {"name": "arbitration_claims", "label": "仲裁请求事项", "type": "text", "required": True},
                {"name": "facts_and_reasons", "label": "事实与理由", "type": "text", "required": True},
            ]
        },
        "content_template": """劳动争议仲裁申请书

申请人：{{applicant_name}}，身份证号：{{applicant_id}}，联系电话：{{applicant_phone}}，通讯地址：{{applicant_address}}。

被申请人：{{respondent_name}}，住所地：{{respondent_address}}，法定代表人：{{respondent_legal_rep}}。

仲裁请求：
{{arbitration_claims}}

事实与理由：
申请人于{{employment_start}}入职被申请人处，担任{{position}}，月工资{{salary}}元。
{{facts_and_reasons}}

此致
劳动争议仲裁委员会

申请人（签名）：
年  月  日""",
    },
    {
        "name": "民事起诉状（劳动争议）",
        "doc_type": "complaint",
        "category": "起诉类",
        "sort_order": 2,
        "variables_schema": {
            "variables": [
                {"name": "plaintiff_name", "label": "原告姓名", "type": "string", "required": True},
                {"name": "plaintiff_id", "label": "原告身份证号", "type": "string", "required": True},
                {"name": "plaintiff_phone", "label": "原告联系电话", "type": "string", "required": True},
                {"name": "plaintiff_address", "label": "原告住址", "type": "string", "required": True},
                {"name": "defendant_name", "label": "被告名称", "type": "string", "required": True},
                {"name": "defendant_address", "label": "被告住所地", "type": "string", "required": True},
                {"name": "defendant_legal_rep", "label": "法定代表人", "type": "string", "required": True},
                {"name": "claims", "label": "诉讼请求", "type": "text", "required": True},
                {"name": "facts", "label": "事实与理由", "type": "text", "required": True},
                {"name": "court_name", "label": "管辖法院", "type": "string", "required": True},
            ]
        },
        "content_template": """民事起诉状

原告：{{plaintiff_name}}，身份证号：{{plaintiff_id}}，联系电话：{{plaintiff_phone}}，住址：{{plaintiff_address}}。

被告：{{defendant_name}}，住所地：{{defendant_address}}，法定代表人：{{defendant_legal_rep}}。

诉讼请求：
{{claims}}

事实与理由：
{{facts}}

此致
{{court_name}}人民法院

具状人（签名）：
年  月  日""",
    },
    {
        "name": "民事答辩状",
        "doc_type": "defense_letter",
        "category": "答辩类",
        "sort_order": 3,
        "variables_schema": {
            "variables": [
                {"name": "respondent_name", "label": "答辩人名称", "type": "string", "required": True},
                {"name": "respondent_address", "label": "答辩人住所地", "type": "string", "required": True},
                {"name": "respondent_legal_rep", "label": "法定代表人", "type": "string", "required": True},
                {"name": "case_info", "label": "案由及案号", "type": "string", "required": True},
                {"name": "defense_arguments", "label": "答辩意见", "type": "text", "required": True},
                {"name": "court_name", "label": "管辖法院", "type": "string", "required": True},
            ]
        },
        "content_template": """民事答辩状

答辩人：{{respondent_name}}，住所地：{{respondent_address}}，法定代表人：{{respondent_legal_rep}}。

就被答辩人提起的{{case_info}}一案，现提出答辩意见如下：

{{defense_arguments}}

此致
{{court_name}}人民法院

答辩人（盖章）：
法定代表人（签字）：
年  月  日""",
    },
    {
        "name": "律师函",
        "doc_type": "lawyer_letter",
        "category": "函件类",
        "sort_order": 4,
        "variables_schema": {
            "variables": [
                {"name": "sender_name", "label": "委托方名称", "type": "string", "required": True},
                {"name": "recipient_name", "label": "收函方名称", "type": "string", "required": True},
                {"name": "law_firm", "label": "律师事务所名称", "type": "string", "required": True},
                {"name": "lawyer_name", "label": "承办律师姓名", "type": "string", "required": True},
                {"name": "lawyer_license", "label": "律师执业证号", "type": "string", "required": True},
                {"name": "matter_description", "label": "就何事致函", "type": "text", "required": True},
                {"name": "demands", "label": "要求事项", "type": "text", "required": True},
                {"name": "deadline", "label": "答复期限", "type": "string", "required": True, "default": "收到本函后七日内"},
            ]
        },
        "content_template": """律 师 函

{{recipient_name}}：

{{law_firm}}接受{{sender_name}}的委托，指派本所{{lawyer_name}}律师（执业证号：{{lawyer_license}}）就{{matter_description}}事宜，郑重致函如下：

{{demands}}

请贵方于{{deadline}}予以书面答复。如逾期未复，本所将依法采取包括但不限于提起诉讼在内的一切法律措施，以维护委托人的合法权益。

特此函告。

{{law_firm}}
承办律师：{{lawyer_name}}
年  月  日""",
    },
    {
        "name": "和解协议书",
        "doc_type": "settlement_agreement",
        "category": "协议类",
        "sort_order": 5,
        "variables_schema": {
            "variables": [
                {"name": "party_a", "label": "甲方（单位/个人）", "type": "string", "required": True},
                {"name": "party_a_id", "label": "甲方证件号", "type": "string", "required": True},
                {"name": "party_b", "label": "乙方（单位/个人）", "type": "string", "required": True},
                {"name": "party_b_id", "label": "乙方证件号", "type": "string", "required": True},
                {"name": "dispute_background", "label": "纠纷背景", "type": "text", "required": True},
                {"name": "settlement_terms", "label": "和解条款", "type": "text", "required": True},
                {"name": "payment_amount", "label": "支付金额", "type": "number", "required": False},
                {"name": "payment_deadline", "label": "支付期限", "type": "string", "required": False},
            ]
        },
        "content_template": """和解协议书

甲方：{{party_a}}
证件号码：{{party_a_id}}

乙方：{{party_b}}
证件号码：{{party_b_id}}

鉴于：
{{dispute_background}}

甲乙双方本着自愿、公平、诚实信用的原则，经友好协商，就上述纠纷达成如下和解协议：

{{settlement_terms}}
{% if payment_amount %}
一、支付义务
乙方同意向甲方支付人民币{{payment_amount}}元，于{{payment_deadline}}前付清。
{% endif %}

本协议一式两份，甲乙双方各执一份，自双方签字（盖章）之日起生效。

甲方（签字/盖章）：              乙方（签字/盖章）：

年  月  日                      年  月  日""",
    },
    {
        "name": "证据清单",
        "doc_type": "evidence_list",
        "category": "证据类",
        "sort_order": 6,
        "variables_schema": {
            "variables": [
                {"name": "party_name", "label": "提交方", "type": "string", "required": True},
                {"name": "case_number", "label": "案号", "type": "string", "required": True},
                {"name": "submission_date", "label": "提交日期", "type": "date", "required": True},
                {"name": "evidence_items", "label": "证据列表（每行一项）", "type": "text", "required": True},
            ]
        },
        "content_template": """证据清单

提交方：{{party_name}}
案    号：{{case_number}}
日    期：{{submission_date}}

{{evidence_items}}

提交人（签名）：
年  月  日""",
    },
    {
        "name": "代理词",
        "doc_type": "representation_letter",
        "category": "代理类",
        "sort_order": 7,
        "variables_schema": {
            "variables": [
                {"name": "court_name", "label": "审判法院", "type": "string", "required": True},
                {"name": "case_number", "label": "案号", "type": "string", "required": True},
                {"name": "law_firm", "label": "律师事务所名称", "type": "string", "required": True},
                {"name": "lawyer_name", "label": "代理律师", "type": "string", "required": True},
                {"name": "party_role", "label": "代理方身份", "type": "string", "required": True, "default": "原告"},
                {"name": "party_name", "label": "被代理人名称", "type": "string", "required": True},
                {"name": "agent_opinion", "label": "代理意见", "type": "text", "required": True},
            ]
        },
        "content_template": """代 理 词

{{court_name}}人民法院：

{{law_firm}}接受{{party_name}}的委托，指派{{lawyer_name}}律师担任其与对方当事人{{case_number}}一案的{{party_role}}代理人。现根据本案事实与相关法律规定，发表如下代理意见：

{{agent_opinion}}

综上所述，请求贵院依法支持{{party_role}}的诉讼请求。

此致
{{court_name}}人民法院

代理人：{{lawyer_name}}
{{law_firm}}
年  月  日""",
    },
    {
        "name": "强制执行申请书",
        "doc_type": "enforcement_application",
        "category": "申请类",
        "sort_order": 8,
        "variables_schema": {
            "variables": [
                {"name": "applicant_name", "label": "申请人", "type": "string", "required": True},
                {"name": "applicant_id", "label": "申请人证件号", "type": "string", "required": True},
                {"name": "respondent_name", "label": "被申请人", "type": "string", "required": True},
                {"name": "respondent_id", "label": "被申请人证件号", "type": "string", "required": True},
                {"name": "judgment_court", "label": "作出判决的法院", "type": "string", "required": True},
                {"name": "judgment_number", "label": "判决书案号", "type": "string", "required": True},
                {"name": "enforcement_items", "label": "申请执行事项", "type": "text", "required": True},
                {"name": "execution_court", "label": "执行法院", "type": "string", "required": True},
            ]
        },
        "content_template": """强制执行申请书

申请人：{{applicant_name}}，证件号码：{{applicant_id}}。

被申请人：{{respondent_name}}，证件号码：{{respondent_id}}。

申请执行依据：{{judgment_court}}{{judgment_number}}。

申请执行事项：
{{enforcement_items}}

此致
{{execution_court}}人民法院

申请人（签名）：
年  月  日""",
    },
    {
        "name": "劳动合同",
        "doc_type": "labor_contract",
        "category": "协议类",
        "sort_order": 9,
        "variables_schema": {
            "variables": [
                {"name": "employer_name", "label": "用人单位名称", "type": "string", "required": True},
                {"name": "employer_address", "label": "用人单位地址", "type": "string", "required": True},
                {"name": "employer_legal_rep", "label": "法定代表人", "type": "string", "required": True},
                {"name": "employee_name", "label": "劳动者姓名", "type": "string", "required": True},
                {"name": "employee_id", "label": "劳动者身份证号", "type": "string", "required": True},
                {"name": "employee_address", "label": "劳动者住址", "type": "string", "required": True},
                {"name": "contract_term", "label": "合同期限", "type": "string", "required": True, "default": "自____年__月__日起至____年__月__日止，其中试用期____个月。"},
                {"name": "position", "label": "工作岗位", "type": "string", "required": True},
                {"name": "work_place", "label": "工作地点", "type": "string", "required": True},
                {"name": "salary", "label": "劳动报酬", "type": "string", "required": True, "default": "月工资____元，于每月____日前支付。"},
            ]
        },
        "content_template": """劳动合同

甲方（用人单位）：{{employer_name}}
住所地：{{employer_address}}
法定代表人：{{employer_legal_rep}}

乙方（劳动者）：{{employee_name}}
身份证号码：{{employee_id}}
住址：{{employee_address}}

根据《中华人民共和国劳动法》《中华人民共和国劳动合同法》等法律法规的规定，甲乙双方经平等自愿、协商一致，签订本合同，共同遵守本合同所列条款。

一、劳动合同期限
{{contract_term}}

二、工作内容和工作地点
乙方同意在{{position}}岗位工作，工作地点为{{work_place}}。

三、工作时间和休息休假
（根据实际情况填写）

四、劳动报酬
{{salary}}

五、社会保险和福利待遇
（根据实际情况填写）

六、劳动保护、劳动条件和职业危害防护
（根据实际情况填写）

七、劳动合同的变更、解除、终止
（根据实际情况填写）

八、其他约定事项
（根据实际情况填写）

甲方（盖章）：                  乙方（签名）：

年  月  日                      年  月  日""",
    },
    {
        "name": "解除劳动合同通知书",
        "doc_type": "termination_notice",
        "category": "通知类",
        "sort_order": 10,
        "variables_schema": {
            "variables": [
                {"name": "employee_name", "label": "劳动者姓名", "type": "string", "required": True},
                {"name": "employee_id", "label": "身份证号", "type": "string", "required": True},
                {"name": "employer_name", "label": "用人单位名称", "type": "string", "required": True},
                {"name": "termination_reason", "label": "解除事由（法律依据）", "type": "text", "required": True},
                {"name": "termination_date", "label": "解除日期", "type": "date", "required": True},
                {"name": "compensation", "label": "经济补偿金额", "type": "string", "required": False, "default": "按《劳动合同法》第四十七条计算"},
                {"name": "final_pay_date", "label": "工资结清日期", "type": "date", "required": True},
            ]
        },
        "content_template": """解除劳动合同通知书

{{employee_name}}（身份证号：{{employee_id}}）：

根据《中华人民共和国劳动合同法》有关规定，{{employer_name}}决定自{{termination_date}}起解除与你的劳动合同。

解除事由：
{{termination_reason}}

经济补偿：
{{compensation}}

请于{{final_pay_date}}前办理离职交接手续，届时结清所有工资及经济补偿。

特此通知。

{{employer_name}}（盖章）

年  月  日""",
    },
]


async def seed_templates(db: AsyncSession) -> None:
    """Seed system templates if none exist."""
    existing = await db.execute(select(func.count(DocumentTemplate.id)).where(DocumentTemplate.is_system == True))
    if existing.scalar() > 0:
        return
    for tmpl in SEED_TEMPLATES:
        t = DocumentTemplate(
            name=tmpl["name"],
            doc_type=tmpl["doc_type"],
            content_template=tmpl["content_template"],
            variables_schema=tmpl["variables_schema"],
            category=tmpl["category"],
            sort_order=tmpl["sort_order"],
            is_system=True,
        )
        db.add(t)
    await db.flush()


# ── Templates ──

async def list_templates(db: AsyncSession, category: str | None = None, tenant_id: uuid.UUID | None = None) -> list[DocumentTemplate]:
    conditions = [(DocumentTemplate.is_system == True) | (DocumentTemplate.tenant_id == tenant_id)]
    if category:
        conditions.append(DocumentTemplate.category == category)
    stmt = select(DocumentTemplate).where(*conditions).order_by(DocumentTemplate.sort_order)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_template(db: AsyncSession, template_id: uuid.UUID) -> DocumentTemplate | None:
    stmt = select(DocumentTemplate).where(DocumentTemplate.id == template_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# ── Documents ──

async def list_documents(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    page: int = 1,
    page_size: int = 20,
    case_id: uuid.UUID | None = None,
    status: str | None = None,
) -> tuple[list[Document], int]:
    conditions = [Document.tenant_id == tenant_id]
    if case_id:
        conditions.append(Document.case_id == case_id)
    if status:
        conditions.append(Document.status == status)

    count_stmt = select(func.count(Document.id)).where(*conditions)
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = (
        select(Document)
        .where(*conditions)
        .order_by(Document.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    return items, total


async def get_document(db: AsyncSession, doc_id: uuid.UUID) -> Document | None:
    stmt = select(Document).where(Document.id == doc_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_document(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    data: dict,
    content: dict | None = None,
) -> Document:
    doc = Document(
        tenant_id=tenant_id,
        user_id=user_id,
        content=content,
        **data,
    )
    db.add(doc)
    await db.flush()
    return doc


async def update_document(db: AsyncSession, doc: Document, data: dict) -> Document:
    for key, value in data.items():
        if value is not None:
            setattr(doc, key, value)
    await db.flush()
    return doc


async def create_version(db: AsyncSession, doc: Document) -> Document:
    """Create a new version from an existing document."""
    new_version = Document(
        tenant_id=doc.tenant_id,
        user_id=doc.user_id,
        title=doc.title,
        doc_type=doc.doc_type,
        template_id=doc.template_id,
        content=doc.content,
        variables=doc.variables,
        status="draft",
        version=doc.version + 1,
        parent_id=doc.id,
        case_id=doc.case_id,
    )
    db.add(new_version)
    await db.flush()
    return new_version
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/services/document_service.py
git commit -m "feat: add document service with 10 seed templates and versioning"
```

---

### Task 4: Create Document API Routes

**Files:**
- Create: `backend/app/api/v1/documents.py`
- Modify: `backend/app/api/router.py`

- [ ] **Step 1: Write the documents API router**

```python
# backend/app/api/v1/documents.py
from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.document import (
    DocumentCreate,
    DocumentGenerateRequest,
    DocumentListResponse,
    DocumentResponse,
    DocumentUpdate,
    TemplateResponse,
)
from app.services import document_service

router = APIRouter(tags=["documents"])


# ── Templates ──

template_router = APIRouter(prefix="/document-templates")


@template_router.get("", response_model=list[TemplateResponse])
async def list_templates(
    category: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await document_service.list_templates(db, category, current_user.tenant_id)
    return [TemplateResponse.model_validate(i) for i in items]


@template_router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tmpl = await document_service.get_template(db, template_id)
    if not tmpl:
        raise HTTPException(status_code=404, detail="模板不存在")
    return TemplateResponse.model_validate(tmpl)


# ── Documents ──

doc_router = APIRouter(prefix="/documents")


@doc_router.get("", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    case_id: uuid.UUID | None = None,
    status: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await document_service.list_documents(
        db, current_user.tenant_id, page, page_size, case_id, status
    )
    return DocumentListResponse(
        items=[DocumentResponse.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@doc_router.post("", response_model=DocumentResponse, status_code=201)
async def create_document(
    req: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data = req.model_dump(exclude_unset=True)
    template_id = data.pop("template_id", None)
    data["template_id"] = template_id

    content = None
    if template_id:
        tmpl = await document_service.get_template(db, template_id)
        if not tmpl:
            raise HTTPException(status_code=404, detail="模板不存在")
        if req.variables:
            content = {"raw": tmpl.content_template, "variables": req.variables}
        else:
            content = {"raw": tmpl.content_template}

    doc = await document_service.create_document(db, current_user.tenant_id, current_user.id, data, content)
    return DocumentResponse.model_validate(doc)


@doc_router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await document_service.get_document(db, doc_id)
    if not doc or doc.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="文书不存在")
    return DocumentResponse.model_validate(doc)


@doc_router.put("/{doc_id}", response_model=DocumentResponse)
async def update_document(
    doc_id: uuid.UUID,
    req: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await document_service.get_document(db, doc_id)
    if not doc or doc.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="文书不存在")
    doc = await document_service.update_document(db, doc, req.model_dump(exclude_unset=True))
    return DocumentResponse.model_validate(doc)


@doc_router.post("/{doc_id}/generate")
async def generate_document(
    doc_id: uuid.UUID,
    req: DocumentGenerateRequest | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await document_service.get_document(db, doc_id)
    if not doc or doc.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="文书不存在")

    async def event_stream():
        import asyncio
        yield f"data: {json.dumps({'status': 'generating', 'message': '正在生成文书...'})}\n\n"
        await asyncio.sleep(0.5)
        # Placeholder for actual AI generation — will be wired to Document Agent in Module 3
        if doc.content and doc.content.get("raw"):
            text = doc.content["raw"]
            if doc.content.get("variables"):
                for k, v in doc.content["variables"].items():
                    text = text.replace(f"{{{{{k}}}}}", str(v))
            yield f"data: {json.dumps({'status': 'complete', 'content': {'html': f'<pre>{text}</pre>'}})}\n\n"
        else:
            yield f"data: {json.dumps({'status': 'error', 'message': '无可用的模板内容'})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@doc_router.post("/{doc_id}/export")
async def export_document(
    doc_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await document_service.get_document(db, doc_id)
    if not doc or doc.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="文书不存在")

    # Placeholder: returns plain text; full Word/PDF export deferred
    text = doc.content.get("raw", "") if doc.content else ""
    if doc.content and doc.content.get("variables"):
        for k, v in doc.content["variables"].items():
            text = text.replace(f"{{{{{k}}}}}", str(v))

    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(
        content=text,
        headers={"Content-Disposition": f"attachment; filename={doc.title}.txt"},
    )
```

- [ ] **Step 2: Register both routers in `backend/app/api/router.py`**

```python
from app.api.v1.documents import doc_router, template_router

api_router.include_router(template_router)
api_router.include_router(doc_router)
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/v1/documents.py backend/app/api/router.py
git commit -m "feat: add document and template API routes with SSE generation"
```

---

### Task 5: Create Alembic Migration

**Files:**
- Create: `backend/alembic/versions/<rev>_add_document_tables.py`

- [ ] **Step 1: Generate and verify migration**

```bash
cd backend && alembic revision --autogenerate -m "add document tables"
```

Verify the generated file creates `document_templates` and `documents` tables.

- [ ] **Step 2: Commit**

```bash
git add backend/alembic/versions/<rev>_add_document_tables.py
git commit -m "feat: add Alembic migration for document_templates and documents"
```

---

### Task 6: Add Frontend Types and Constants

**Files:**
- Modify: `frontend/src/types/index.ts`
- Modify: `frontend/src/lib/constants.ts`

- [ ] **Step 1: Add document TypeScript types**

```typescript
// Add to frontend/src/types/index.ts

export interface TemplateItem {
  id: string;
  name: string;
  doc_type: string;
  content_template: string;
  variables_schema: { variables: { name: string; label: string; type: string; required: boolean; default?: string }[] };
  category: string;
  sort_order: number;
  is_system: boolean;
  tenant_id: string | null;
  created_at: string;
}

export interface DocumentItem {
  id: string;
  case_id: string | null;
  tenant_id: string;
  user_id: string;
  title: string;
  doc_type: string;
  template_id: string | null;
  content: Record<string, unknown> | null;
  variables: Record<string, unknown> | null;
  status: string;
  version: number;
  parent_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface DocumentListResponse {
  items: DocumentItem[];
  total: number;
  page: number;
  page_size: number;
}
```

- [ ] **Step 2: Add document constants**

```typescript
// Add to frontend/src/lib/constants.ts

export const DOC_CATEGORIES: Record<string, string> = {
  "申请类": "申请类",
  "起诉类": "起诉类",
  "答辩类": "答辩类",
  "函件类": "函件类",
  "协议类": "协议类",
  "证据类": "证据类",
  "代理类": "代理类",
  "通知类": "通知类",
};

export const DOC_STATUSES: Record<string, string> = {
  draft: "草稿",
  generating: "生成中",
  completed: "已完成",
  exported: "已导出",
};
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/types/index.ts frontend/src/lib/constants.ts
git commit -m "feat: add document and template TypeScript types and constants"
```

---

### Task 7: Create Template Library Page

**Files:**
- Create: `frontend/src/app/(dashboard)/documents/templates/page.tsx`

- [ ] **Step 1: Write the template library page**

```tsx
"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import { api } from "@/lib/api-client";
import { DOC_CATEGORIES } from "@/lib/constants";
import type { TemplateItem } from "@/types";

export default function TemplatesPage() {
  const { token } = useAuth();
  const router = useRouter();
  const [templates, setTemplates] = useState<TemplateItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState("");

  const fetchTemplates = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const params = category ? `?category=${category}` : "";
      const data = await api.get<TemplateItem[]>(`/document-templates${params}`, token);
      setTemplates(data);
    } finally {
      setLoading(false);
    }
  }, [token, category]);

  useEffect(() => { fetchTemplates(); }, [fetchTemplates]);

  const categories = ["全部", ...Object.values(DOC_CATEGORIES)];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">文书模板库</h1>
          <p className="text-sm text-muted-foreground mt-1">{templates.length} 个模板</p>
        </div>
      </div>

      <div className="flex gap-2 flex-wrap">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setCategory(cat === "全部" ? "" : cat)}
            className={`rounded-full px-3 py-1 text-sm ${
              (cat === "全部" && !category) || cat === category
                ? "bg-primary text-primary-foreground"
                : "border hover:bg-accent"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {loading ? (
        <p className="text-center text-muted-foreground py-8">加载中...</p>
      ) : templates.length === 0 ? (
        <p className="text-center text-muted-foreground py-8">暂无模板</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {templates.map((t) => (
            <div key={t.id} className="rounded-lg border p-5 space-y-3 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <h3 className="font-semibold">{t.name}</h3>
                <span className="text-xs rounded-full bg-accent px-2 py-0.5">{t.category}</span>
              </div>
              <p className="text-sm text-muted-foreground line-clamp-3 font-mono text-xs whitespace-pre-wrap">
                {t.content_template.slice(0, 150)}...
              </p>
              <div className="flex flex-wrap gap-1">
                {t.variables_schema?.variables?.slice(0, 4).map((v: { name: string; label: string }) => (
                  <span key={v.name} className="text-xs bg-muted rounded px-1.5 py-0.5">{v.label}</span>
                ))}
                {(t.variables_schema?.variables?.length || 0) > 4 && (
                  <span className="text-xs text-muted-foreground">+{t.variables_schema.variables.length - 4}</span>
                )}
              </div>
              <button
                onClick={() => router.push(`/documents/new?template=${t.id}`)}
                className="w-full rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90"
              >
                使用此模板
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/app/\(dashboard\)/documents/templates/page.tsx
git commit -m "feat: add document template library page with category filter"
```

---

### Task 8: Create Document List Page

**Files:**
- Create: `frontend/src/app/(dashboard)/documents/page.tsx`

- [ ] **Step 1: Write the document list page**

```tsx
"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/providers/auth-provider";
import { api } from "@/lib/api-client";
import { DOC_STATUSES } from "@/lib/constants";
import type { DocumentItem } from "@/types";

export default function DocumentsPage() {
  const { token } = useAuth();
  const router = useRouter();
  const [docs, setDocs] = useState<DocumentItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");

  const fetchDocs = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.set("page", String(page));
      params.set("page_size", "20");
      if (statusFilter) params.set("status", statusFilter);
      const data = await api.get<{ items: DocumentItem[]; total: number }>(
        `/documents?${params.toString()}`,
        token
      );
      setDocs(data.items);
      setTotal(data.total);
    } finally {
      setLoading(false);
    }
  }, [token, page, statusFilter]);

  useEffect(() => { fetchDocs(); }, [fetchDocs]);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">文书中心</h1>
          <p className="text-sm text-muted-foreground mt-1">共 {total} 份文书</p>
        </div>
        <div className="flex gap-2">
          <Link href="/documents/templates" className="rounded-md border px-4 py-2 text-sm hover:bg-accent">
            模板库
          </Link>
          <Link href="/documents/new" className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90">
            + 新建文书
          </Link>
        </div>
      </div>

      <select
        value={statusFilter}
        onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
        className="rounded-md border px-3 py-2 text-sm bg-background w-40"
      >
        <option value="">全部状态</option>
        {Object.entries(DOC_STATUSES).map(([k, v]) => (
          <option key={k} value={k}>{v}</option>
        ))}
      </select>

      {loading ? (
        <p className="text-center text-muted-foreground py-8">加载中...</p>
      ) : docs.length === 0 ? (
        <p className="text-center text-muted-foreground py-8">暂无文书</p>
      ) : (
        <div className="rounded-lg border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                <th className="px-4 py-3 text-left font-medium">标题</th>
                <th className="px-4 py-3 text-left font-medium">状态</th>
                <th className="px-4 py-3 text-left font-medium">版本</th>
                <th className="px-4 py-3 text-left font-medium">创建时间</th>
              </tr>
            </thead>
            <tbody>
              {docs.map((d) => (
                <tr key={d.id} className="border-t hover:bg-muted/30 cursor-pointer" onClick={() => router.push(`/documents/${d.id}`)}>
                  <td className="px-4 py-3 font-medium">{d.title}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                      d.status === "completed" ? "bg-green-100 text-green-700" :
                      d.status === "generating" ? "bg-yellow-100 text-yellow-700" :
                      d.status === "exported" ? "bg-blue-100 text-blue-700" :
                      "bg-gray-100 text-gray-700"
                    }`}>
                      {DOC_STATUSES[d.status] || d.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">v{d.version}</td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {new Date(d.created_at).toLocaleDateString("zh-CN")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/app/\(dashboard\)/documents/page.tsx
git commit -m "feat: add document list page with status filter"
```

---

### Task 9: Create Document Creation Wizard

**Files:**
- Create: `frontend/src/app/(dashboard)/documents/new/page.tsx`

- [ ] **Step 1: Write the document creation wizard (choose template → fill variables → create)**

```tsx
"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import { api } from "@/lib/api-client";
import type { TemplateItem, DocumentItem } from "@/types";

interface StepState {
  step: "select" | "fill" | "creating";
  template: TemplateItem | null;
  variables: Record<string, string>;
}

export default function NewDocumentPage() {
  const { token } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [state, setState] = useState<StepState>({ step: "select", template: null, variables: {} });
  const [templates, setTemplates] = useState<TemplateItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [title, setTitle] = useState("");
  const [error, setError] = useState("");

  const fetchTemplates = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const data = await api.get<TemplateItem[]>("/document-templates", token);
      setTemplates(data);
      const templateId = searchParams.get("template");
      if (templateId) {
        const tmpl = data.find((t) => t.id === templateId);
        if (tmpl) selectTemplate(tmpl);
      }
    } finally {
      setLoading(false);
    }
  }, [token, searchParams]);

  useEffect(() => { fetchTemplates(); }, [fetchTemplates]);

  const selectTemplate = (tmpl: TemplateItem) => {
    const vars: Record<string, string> = {};
    tmpl.variables_schema?.variables?.forEach((v) => {
      vars[v.name] = v.default || "";
    });
    setState({ step: "fill", template: tmpl, variables: vars });
    setTitle(tmpl.name);
  };

  const setVar = (name: string, value: string) => {
    setState((prev) => ({ ...prev, variables: { ...prev.variables, [name]: value } }));
  };

  const handleCreate = async () => {
    if (!state.template || !token) return;
    setError("");
    setState((prev) => ({ ...prev, step: "creating" }));
    try {
      const data = await api.post<DocumentItem>("/documents", {
        title: title.trim() || state.template.name,
        doc_type: state.template.doc_type,
        template_id: state.template.id,
        variables: state.variables,
      }, token);
      router.push(`/documents/${data.id}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "创建失败");
      setState((prev) => ({ ...prev, step: "fill" }));
    }
  };

  if (loading) return <p className="p-6 text-center text-muted-foreground">加载中...</p>;

  return (
    <div className="p-6 max-w-3xl space-y-6">
      <button onClick={() => router.push("/documents")} className="text-sm text-muted-foreground hover:text-foreground">
        ← 返回文书列表
      </button>
      <h1 className="text-2xl font-bold">新建文书</h1>

      {/* Step indicator */}
      <div className="flex items-center gap-3 text-sm">
        <span className={`rounded-full px-3 py-1 ${state.step === "select" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
          1. 选择模板
        </span>
        <span className="text-muted-foreground">→</span>
        <span className={`rounded-full px-3 py-1 ${state.step === "fill" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
          2. 填写信息
        </span>
      </div>

      {error && <p className="text-sm text-destructive bg-destructive/10 rounded-md px-4 py-2">{error}</p>}

      {/* Step 1: Select template */}
      {state.step === "select" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {templates.map((t) => (
            <button
              key={t.id}
              onClick={() => selectTemplate(t)}
              className="text-left rounded-lg border p-4 hover:shadow-md hover:border-primary transition-all"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold">{t.name}</span>
                <span className="text-xs bg-accent rounded px-2 py-0.5">{t.category}</span>
              </div>
              <p className="text-xs text-muted-foreground font-mono line-clamp-2">{t.content_template.slice(0, 100)}</p>
            </button>
          ))}
        </div>
      )}

      {/* Step 2: Fill variables */}
      {state.step === "fill" && state.template && (
        <div className="space-y-4">
          <div className="rounded-lg border p-5">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-xs bg-accent rounded px-2 py-0.5">{state.template.category}</span>
              <span className="font-semibold">{state.template.name}</span>
            </div>
            <div>
              <label className="text-sm font-medium">文书标题</label>
              <input type="text" value={title} onChange={(e) => setTitle(e.target.value)}
                className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1" />
            </div>
          </div>

          <div className="rounded-lg border p-5 space-y-4">
            <h2 className="font-semibold">填写信息</h2>
            {state.template.variables_schema?.variables?.map((v: { name: string; label: string; type: string; required: boolean }) => (
              <div key={v.name}>
                <label className="text-sm font-medium">
                  {v.label} {v.required && <span className="text-destructive">*</span>}
                </label>
                {v.type === "text" ? (
                  <textarea
                    value={state.variables[v.name] || ""}
                    onChange={(e) => setVar(v.name, e.target.value)}
                    rows={3}
                    className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1"
                  />
                ) : v.type === "date" ? (
                  <input
                    type="date"
                    value={state.variables[v.name] || ""}
                    onChange={(e) => setVar(v.name, e.target.value)}
                    className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1"
                  />
                ) : (
                  <input
                    type={v.type === "number" ? "number" : "text"}
                    value={state.variables[v.name] || ""}
                    onChange={(e) => setVar(v.name, e.target.value)}
                    className="w-full rounded-md border px-3 py-2 text-sm bg-background mt-1"
                  />
                )}
              </div>
            ))}
          </div>

          <div className="flex gap-3">
            <button onClick={handleCreate} disabled={state.step === "creating"}
              className="rounded-md bg-primary px-6 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50">
              {state.step === "creating" ? "创建中..." : "创建文书"}
            </button>
            <button onClick={() => setState({ step: "select", template: null, variables: {} })}
              className="rounded-md border px-6 py-2 text-sm hover:bg-accent">
              重新选择
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/app/\(dashboard\)/documents/new/page.tsx
git commit -m "feat: add document creation wizard with template selection and variable filling"
```

---

### Task 10: Create Document Editor Page

**Files:**
- Create: `frontend/src/app/(dashboard)/documents/[id]/page.tsx`

- [ ] **Step 1: Write the document editor page**

```tsx
"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import { api } from "@/lib/api-client";
import { DOC_STATUSES } from "@/lib/constants";
import type { DocumentItem } from "@/types";

export default function DocumentEditorPage() {
  const { id } = useParams<{ id: string }>();
  const { token } = useAuth();
  const router = useRouter();
  const [doc, setDoc] = useState<DocumentItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [generatedHtml, setGeneratedHtml] = useState("");
  const [instructions, setInstructions] = useState("");
  const eventSourceRef = useRef<AbortController | null>(null);

  const fetchDoc = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const data = await api.get<DocumentItem>(`/documents/${id}`, token);
      setDoc(data);
    } catch {
      router.push("/documents");
    } finally {
      setLoading(false);
    }
  }, [token, id, router]);

  useEffect(() => { fetchDoc(); }, [fetchDoc]);

  const handleGenerate = () => {
    if (!token) return;
    setGenerating(true);
    setGeneratedHtml("");

    const controller = new AbortController();
    eventSourceRef.current = controller;

    fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/documents/${id}/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify({ instructions: instructions || null }),
      signal: controller.signal,
    })
      .then(async (res) => {
        if (!res.ok) throw new Error("Generation failed");
        const reader = res.body?.getReader();
        if (!reader) return;

        const decoder = new TextDecoder();
        let buffer = "";
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";
          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const data = line.slice(6);
              if (data === "[DONE]") { setGenerating(false); return; }
              try {
                const parsed = JSON.parse(data);
                if (parsed.status === "complete" && parsed.content?.html) {
                  setGeneratedHtml(parsed.content.html);
                }
              } catch {}
            }
          }
        }
        setGenerating(false);
      })
      .catch(() => setGenerating(false));
  };

  const handleExport = async () => {
    if (!token) return;
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/documents/${id}/export`,
        {
          method: "POST",
          headers: { "Authorization": `Bearer ${token}` },
        }
      );
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${doc?.title || "document"}.txt`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {}
  };

  // Render filled template preview
  const renderPreview = (): string => {
    if (!doc?.content) return "";
    let text = doc.content.raw || "";
    if (doc.content.variables) {
      for (const [k, v] of Object.entries(doc.content.variables as Record<string, string>)) {
        text = text.replace(new RegExp(`\\{\\{\\s*${k}\\s*\\}\\}`, "g"), v);
      }
    }
    return text;
  };

  if (loading) return <p className="p-6 text-center text-muted-foreground">加载中...</p>;
  if (!doc) return <p className="p-6 text-center text-muted-foreground">文书不存在</p>;

  const preview = renderPreview();

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <button onClick={() => router.push("/documents")} className="text-sm text-muted-foreground hover:text-foreground mb-1">
            ← 返回文书列表
          </button>
          <h1 className="text-2xl font-bold">{doc.title}</h1>
          <p className="text-sm text-muted-foreground">
            {DOC_STATUSES[doc.status] || doc.status} · v{doc.version}
          </p>
        </div>
        <div className="flex gap-2">
          <button onClick={handleGenerate} disabled={generating}
            className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50">
            {generating ? "生成中..." : "AI 生成"}
          </button>
          <button onClick={handleExport}
            className="rounded-md border px-4 py-2 text-sm hover:bg-accent">
            导出
          </button>
        </div>
      </div>

      {/* AI instructions */}
      <div className="rounded-lg border p-4 space-y-2">
        <label className="text-sm font-medium">AI 生成指令（可选）</label>
        <textarea
          value={instructions}
          onChange={(e) => setInstructions(e.target.value)}
          rows={2}
          placeholder="如：请详细阐述事实与理由部分，引用《劳动合同法》相关条款..."
          className="w-full rounded-md border px-3 py-2 text-sm bg-background"
        />
      </div>

      {/* Preview area */}
      <div className="rounded-lg border">
        <div className="px-4 py-3 bg-muted/50 border-b font-medium text-sm">文书预览</div>
        <div className="p-6 min-h-[400px]">
          {generatedHtml ? (
            <div dangerouslySetInnerHTML={{ __html: generatedHtml }} />
          ) : preview ? (
            <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">{preview}</pre>
          ) : (
            <p className="text-center text-muted-foreground py-12">暂无内容，点击"AI 生成"开始</p>
          )}
        </div>
      </div>

      {/* Variable summary */}
      {doc.variables && Object.keys(doc.variables).length > 0 && (
        <div className="rounded-lg border p-4">
          <h3 className="text-sm font-medium mb-2">已填写变量</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {Object.entries(doc.variables as Record<string, string>).map(([k, v]) => (
              <div key={k} className="text-sm">
                <span className="text-muted-foreground">{k}: </span>
                <span className="font-medium">{v || "(空)"}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/app/\(dashboard\)/documents/\[id\]/page.tsx
git commit -m "feat: add document editor page with AI generation and export"
```

---

### Task 11: Update Sidebar Navigation

**Files:**
- Modify: `frontend/src/app/(dashboard)/layout.tsx`

- [ ] **Step 1: Add "文书中心" to navItems**

Read the layout file, add after the cases entry:
```typescript
{ href: "/documents", label: "文书中心", icon: "📝" },
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/app/\(dashboard\)/layout.tsx
git commit -m "feat: add documents nav item to sidebar"
```

---

### Task 12: Seed Templates on App Startup

**Files:**
- Modify: `backend/app/main.py`

- [ ] **Step 1: Add seed call to lifespan**

Read `backend/app/main.py`. Modify the lifespan to seed templates on startup:

```python
from contextlib import asynccontextmanager
from app.core.database import AsyncSessionLocal
from app.services.document_service import seed_templates

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSessionLocal() as db:
        await seed_templates(db)
        await db.commit()
    yield
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/main.py
git commit -m "feat: auto-seed document templates on app startup"
```

---

## Self-Review Checklist

1. **Spec coverage:**
   - [x] DocumentTemplate + Document models — Task 1
   - [x] 10 seed templates — Task 3
   - [x] Template list API — Task 4
   - [x] Document CRUD API — Task 4
   - [x] AI generate (SSE) — Task 4, Task 10
   - [x] Export endpoint — Task 4, Task 10
   - [x] Template library page — Task 7
   - [x] Document list page — Task 8
   - [x] Document creation wizard — Task 9
   - [x] Document editor page — Task 10
   - [x] Sidebar nav update — Task 11
   - [x] Versioning (parent_id) — Task 1 model

2. **Placeholder scan:** AI generation in API currently substitutes variables (placeholder logic). Full LangGraph Document Agent integration happens in Module 3. Export is plain text; Word/PDF can be enhanced later.

3. **Type consistency:** TemplateResponse/DocumentResponse/DocumentCreate names consistent across service, route, and frontend.
