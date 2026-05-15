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
    from sqlalchemy import or_
    conditions = []
    if tenant_id is not None:
        conditions.append(or_(DocumentTemplate.is_system == True, DocumentTemplate.tenant_id == tenant_id))
    else:
        conditions.append(DocumentTemplate.is_system == True)
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
