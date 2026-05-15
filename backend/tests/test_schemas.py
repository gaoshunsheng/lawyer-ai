"""Comprehensive validation tests for all Phase 2 Pydantic schemas."""

import datetime
import uuid

import pytest
from pydantic import ValidationError

from app.schemas.case import (
    CaseCreate,
    CaseListResponse,
    CaseResponse,
    CaseStatusUpdate,
    CaseUpdate,
    EvidenceCreate,
    EvidenceResponse,
    EvidenceUpdate,
    PersonInfo,
    TimelineCreate,
    TimelineResponse,
    TimelineUpdate,
)
from app.schemas.document import (
    DocumentCreate,
    DocumentGenerateRequest,
    DocumentListResponse,
    DocumentResponse,
    DocumentUpdate,
    TemplateResponse,
)
from app.schemas.favorite import (
    FavoriteCreate,
    FavoriteResponse,
    FavoriteUpdate,
)


# ---------------------------------------------------------------------------
# PersonInfo
# ---------------------------------------------------------------------------

class TestPersonInfo:
    def test_defaults(self):
        p = PersonInfo()
        assert p.name == ""
        assert p.id_number == ""
        assert p.contact == ""

    def test_with_values(self):
        p = PersonInfo(name="张三", id_number="110101199001011234", contact="13800138000")
        assert p.name == "张三"
        assert p.id_number == "110101199001011234"
        assert p.contact == "13800138000"

    def test_rejects_wrong_types(self):
        with pytest.raises(ValidationError):
            PersonInfo(name=123)


# ---------------------------------------------------------------------------
# CaseCreate / CaseUpdate / CaseStatusUpdate / CaseResponse
# ---------------------------------------------------------------------------

class TestCaseSchemas:
    # -- CaseCreate --

    def test_case_create_minimal(self):
        req = CaseCreate(title="劳动争议", case_type="labor_contract")
        assert req.title == "劳动争议"
        assert req.case_type == "labor_contract"
        assert req.plaintiff.name == ""
        assert req.defendant.name == ""
        assert req.claim_amount is None
        assert req.dispute_focus is None
        assert req.assistant_id is None

    def test_case_create_full(self):
        uid = uuid.uuid4()
        req = CaseCreate(
            title="合同纠纷",
            case_type="contract",
            plaintiff=PersonInfo(name="原告", id_number="ID1", contact="c1"),
            defendant=PersonInfo(name="被告", id_number="ID2", contact="c2"),
            claim_amount=50000.0,
            dispute_focus=["违约金", "赔偿"],
            assistant_id=uid,
        )
        assert req.plaintiff.name == "原告"
        assert req.defendant.name == "被告"
        assert req.claim_amount == 50000.0
        assert req.dispute_focus == ["违约金", "赔偿"]
        assert req.assistant_id == uid

    def test_case_create_requires_title(self):
        with pytest.raises(ValidationError):
            CaseCreate(case_type="labor_contract")

    def test_case_create_requires_case_type(self):
        with pytest.raises(ValidationError):
            CaseCreate(title="测试案件")

    def test_case_create_title_max_length(self):
        req = CaseCreate(title="x" * 200, case_type="other")
        assert len(req.title) == 200

    def test_case_create_title_exceeds_max_length(self):
        with pytest.raises(ValidationError):
            CaseCreate(title="x" * 201, case_type="other")

    def test_case_create_rejects_wrong_type_for_claim_amount(self):
        with pytest.raises(ValidationError):
            CaseCreate(title="测试", case_type="other", claim_amount="not_a_number")

    # -- CaseUpdate --

    def test_case_update_all_none(self):
        req = CaseUpdate()
        assert req.title is None
        assert req.case_type is None
        assert req.plaintiff is None
        assert req.defendant is None
        assert req.claim_amount is None
        assert req.dispute_focus is None
        assert req.assistant_id is None

    def test_case_update_partial(self):
        req = CaseUpdate(title="新标题", claim_amount=1000.0)
        assert req.title == "新标题"
        assert req.claim_amount == 1000.0
        assert req.case_type is None

    # -- CaseStatusUpdate --

    def test_case_status_update_requires_status(self):
        with pytest.raises(ValidationError):
            CaseStatusUpdate()

    def test_case_status_update_valid(self):
        req = CaseStatusUpdate(status="in_progress")
        assert req.status == "in_progress"

    # -- CaseResponse --

    def test_case_response_from_attributes(self):
        assert CaseResponse.model_config.get("from_attributes") is True

    def test_case_response_requires_all_fields(self):
        with pytest.raises(ValidationError):
            CaseResponse(id=uuid.uuid4())

    def test_case_response_valid(self):
        now = datetime.datetime.now()
        uid = uuid.uuid4()
        resp = CaseResponse(
            id=uid,
            case_number="CASE-001",
            title="测试",
            case_type="other",
            status="draft",
            plaintiff={"name": "张三"},
            defendant={"name": "李四"},
            claim_amount=None,
            dispute_focus=None,
            lawyer_id=uid,
            assistant_id=None,
            tenant_id=uid,
            gantt_data=None,
            ai_analysis=None,
            created_at=now,
            updated_at=now,
        )
        assert resp.case_number == "CASE-001"
        assert resp.plaintiff == {"name": "张三"}


# ---------------------------------------------------------------------------
# Evidence schemas
# ---------------------------------------------------------------------------

class TestEvidenceSchemas:
    def test_evidence_create_requires_title(self):
        with pytest.raises(ValidationError):
            EvidenceCreate(evidence_type="contract")

    def test_evidence_create_requires_evidence_type(self):
        with pytest.raises(ValidationError):
            EvidenceCreate(title="合同原件")

    def test_evidence_create_minimal(self):
        req = EvidenceCreate(title="合同原件", evidence_type="contract")
        assert req.title == "合同原件"
        assert req.evidence_type == "contract"
        assert req.description is None
        assert req.sort_order == 0

    def test_evidence_create_full(self):
        req = EvidenceCreate(
            title="合同原件", evidence_type="contract", description="签署合同", sort_order=5
        )
        assert req.description == "签署合同"
        assert req.sort_order == 5

    def test_evidence_create_title_max_length(self):
        req = EvidenceCreate(title="y" * 200, evidence_type="photo")
        assert len(req.title) == 200

    def test_evidence_create_title_exceeds_max_length(self):
        with pytest.raises(ValidationError):
            EvidenceCreate(title="y" * 201, evidence_type="photo")

    def test_evidence_update_all_none(self):
        req = EvidenceUpdate()
        assert req.title is None
        assert req.evidence_type is None
        assert req.description is None
        assert req.sort_order is None

    def test_evidence_response_from_attributes(self):
        assert EvidenceResponse.model_config.get("from_attributes") is True


# ---------------------------------------------------------------------------
# Timeline schemas
# ---------------------------------------------------------------------------

class TestTimelineSchemas:
    def test_timeline_create_requires_event_date(self):
        with pytest.raises(ValidationError):
            TimelineCreate(event_type="milestone", title="开庭")

    def test_timeline_create_requires_event_type(self):
        with pytest.raises(ValidationError):
            TimelineCreate(title="开庭", event_date=datetime.date(2026, 1, 1))

    def test_timeline_create_requires_title(self):
        with pytest.raises(ValidationError):
            TimelineCreate(event_type="milestone", event_date=datetime.date(2026, 1, 1))

    def test_timeline_create_minimal(self):
        req = TimelineCreate(
            event_type="milestone", title="立案", event_date=datetime.date(2026, 5, 15)
        )
        assert req.event_type == "milestone"
        assert req.title == "立案"
        assert req.event_date == datetime.date(2026, 5, 15)
        assert req.description is None

    def test_timeline_create_full(self):
        req = TimelineCreate(
            event_type="hearing",
            title="一审开庭",
            description="第一次开庭审理",
            event_date=datetime.date(2026, 6, 1),
        )
        assert req.description == "第一次开庭审理"

    def test_timeline_create_title_max_length(self):
        req = TimelineCreate(
            event_type="milestone", title="z" * 200, event_date=datetime.date(2026, 1, 1)
        )
        assert len(req.title) == 200

    def test_timeline_create_title_exceeds_max_length(self):
        with pytest.raises(ValidationError):
            TimelineCreate(
                event_type="milestone", title="z" * 201, event_date=datetime.date(2026, 1, 1)
            )

    def test_timeline_create_rejects_invalid_date(self):
        with pytest.raises(ValidationError):
            TimelineCreate(event_type="milestone", title="测试", event_date="not_a_date")

    def test_timeline_update_all_none(self):
        req = TimelineUpdate()
        assert req.event_type is None
        assert req.title is None
        assert req.description is None
        assert req.event_date is None

    def test_timeline_response_from_attributes(self):
        assert TimelineResponse.model_config.get("from_attributes") is True


# ---------------------------------------------------------------------------
# Document schemas
# ---------------------------------------------------------------------------

class TestDocumentSchemas:
    # -- TemplateResponse --

    def test_template_response_from_attributes(self):
        assert TemplateResponse.model_config.get("from_attributes") is True

    # -- DocumentCreate --

    def test_document_create_requires_title(self):
        with pytest.raises(ValidationError):
            DocumentCreate(doc_type="complaint")

    def test_document_create_requires_doc_type(self):
        with pytest.raises(ValidationError):
            DocumentCreate(title="起诉状")

    def test_document_create_minimal(self):
        req = DocumentCreate(title="起诉状", doc_type="complaint")
        assert req.title == "起诉状"
        assert req.doc_type == "complaint"
        assert req.template_id is None
        assert req.case_id is None
        assert req.variables is None

    def test_document_create_full(self):
        tid = uuid.uuid4()
        cid = uuid.uuid4()
        req = DocumentCreate(
            title="起诉状",
            doc_type="complaint",
            template_id=tid,
            case_id=cid,
            variables={"name": "张三", "amount": "50000"},
        )
        assert req.template_id == tid
        assert req.case_id == cid
        assert req.variables == {"name": "张三", "amount": "50000"}

    def test_document_create_title_max_length(self):
        req = DocumentCreate(title="x" * 200, doc_type="contract")
        assert len(req.title) == 200

    def test_document_create_title_exceeds_max_length(self):
        with pytest.raises(ValidationError):
            DocumentCreate(title="x" * 201, doc_type="contract")

    def test_document_create_rejects_invalid_template_id(self):
        with pytest.raises(ValidationError):
            DocumentCreate(title="测试", doc_type="contract", template_id="not_a_uuid")

    def test_document_create_rejects_invalid_case_id(self):
        with pytest.raises(ValidationError):
            DocumentCreate(title="测试", doc_type="contract", case_id="not_a_uuid")

    # -- DocumentUpdate --

    def test_document_update_all_optional(self):
        req = DocumentUpdate()
        assert req.title is None
        assert req.content is None
        assert req.variables is None
        assert req.status is None

    def test_document_update_partial(self):
        req = DocumentUpdate(title="新标题", status="approved")
        assert req.title == "新标题"
        assert req.status == "approved"
        assert req.content is None

    # -- DocumentGenerateRequest --

    def test_document_generate_request_defaults(self):
        req = DocumentGenerateRequest()
        assert req.instructions is None

    def test_document_generate_request_with_instructions(self):
        req = DocumentGenerateRequest(instructions="请根据以下信息起草起诉状")
        assert req.instructions == "请根据以下信息起草起诉状"

    # -- DocumentResponse --

    def test_document_response_from_attributes(self):
        assert DocumentResponse.model_config.get("from_attributes") is True

    def test_document_response_requires_all_fields(self):
        with pytest.raises(ValidationError):
            DocumentResponse(id=uuid.uuid4())

    # -- DocumentListResponse --

    def test_document_list_response_defaults(self):
        now = datetime.datetime.now()
        uid = uuid.uuid4()
        doc = DocumentResponse(
            id=uid,
            case_id=None,
            tenant_id=uid,
            user_id=uid,
            title="测试",
            doc_type="complaint",
            template_id=None,
            content=None,
            variables=None,
            status="draft",
            version=1,
            parent_id=None,
            created_at=now,
            updated_at=now,
        )
        resp = DocumentListResponse(items=[doc], total=1, page=1, page_size=10)
        assert resp.total == 1
        assert len(resp.items) == 1


# ---------------------------------------------------------------------------
# Favorite schemas
# ---------------------------------------------------------------------------

class TestFavoriteSchemas:
    def test_favorite_create_requires_target_type(self):
        with pytest.raises(ValidationError):
            FavoriteCreate(target_id=uuid.uuid4())

    def test_favorite_create_requires_target_id(self):
        with pytest.raises(ValidationError):
            FavoriteCreate(target_type="law")

    def test_favorite_create_minimal(self):
        tid = uuid.uuid4()
        req = FavoriteCreate(target_type="law", target_id=tid)
        assert req.target_type == "law"
        assert req.target_id == tid
        assert req.notes is None

    def test_favorite_create_with_notes(self):
        tid = uuid.uuid4()
        req = FavoriteCreate(target_type="case", target_id=tid, notes="重要案例")
        assert req.notes == "重要案例"

    def test_favorite_create_rejects_invalid_target_id(self):
        with pytest.raises(ValidationError):
            FavoriteCreate(target_type="law", target_id="not_a_uuid")

    def test_favorite_update_defaults(self):
        req = FavoriteUpdate()
        assert req.notes is None

    def test_favorite_update_with_notes(self):
        req = FavoriteUpdate(notes="更新备注")
        assert req.notes == "更新备注"

    def test_favorite_response_from_attributes(self):
        assert FavoriteResponse.model_config.get("from_attributes") is True

    def test_favorite_response_requires_all_fields(self):
        with pytest.raises(ValidationError):
            FavoriteResponse(id=uuid.uuid4())
