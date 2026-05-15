"""Schema validation tests for case-related Pydantic models.

These tests exercise the request/response schemas defined in
app/schemas/case.py without requiring a database connection.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

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


# ===================================================================
# PersonInfo
# ===================================================================

def test_person_info_defaults():
    p = PersonInfo()
    assert p.name == ""
    assert p.id_number == ""
    assert p.contact == ""


def test_person_info_with_values():
    p = PersonInfo(name="张三", id_number="110101199001011234", contact="13800138000")
    assert p.name == "张三"
    assert p.id_number == "110101199001011234"


# ===================================================================
# CaseCreate
# ===================================================================

def test_case_create_requires_title():
    with pytest.raises(ValidationError) as exc_info:
        CaseCreate(case_type="labor_contract")  # missing title
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("title",) for e in errors)


def test_case_create_requires_case_type():
    with pytest.raises(ValidationError) as exc_info:
        CaseCreate(title="测试案件")  # missing case_type
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("case_type",) for e in errors)


def test_case_create_defaults():
    req = CaseCreate(title="测试案件", case_type="labor_contract")
    assert req.plaintiff.name == ""
    assert req.defendant.name == ""
    assert req.claim_amount is None
    assert req.dispute_focus is None
    assert req.assistant_id is None


def test_case_create_full():
    plaintiff = PersonInfo(name="原告", id_number="123", contact="111")
    defendant = PersonInfo(name="被告", id_number="456", contact="222")
    req = CaseCreate(
        title="劳动纠纷案",
        case_type="labor_contract",
        plaintiff=plaintiff,
        defendant=defendant,
        claim_amount=50000.0,
        dispute_focus=["加班费", "经济补偿"],
        assistant_id=uuid.uuid4(),
    )
    assert req.title == "劳动纠纷案"
    assert req.claim_amount == 50000.0
    assert len(req.dispute_focus) == 2


def test_case_create_title_too_long():
    with pytest.raises(ValidationError) as exc_info:
        CaseCreate(title="x" * 201, case_type="labor_contract")
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("title",) for e in errors)


# ===================================================================
# CaseUpdate
# ===================================================================

def test_case_update_all_none():
    req = CaseUpdate()
    assert req.title is None
    assert req.case_type is None
    assert req.plaintiff is None
    assert req.claim_amount is None


def test_case_update_partial():
    req = CaseUpdate(title="新标题", claim_amount=10000.0)
    assert req.title == "新标题"
    assert req.case_type is None
    assert req.claim_amount == 10000.0


# ===================================================================
# CaseStatusUpdate
# ===================================================================

def test_case_status_update_requires_status():
    with pytest.raises(ValidationError):
        CaseStatusUpdate()  # type: ignore[call-arg]


def test_case_status_update_valid():
    req = CaseStatusUpdate(status="active")
    assert req.status == "active"


# ===================================================================
# EvidenceCreate
# ===================================================================

def test_evidence_create_requires_title():
    with pytest.raises(ValidationError) as exc_info:
        EvidenceCreate(evidence_type="contract")  # missing title
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("title",) for e in errors)


def test_evidence_create_requires_evidence_type():
    with pytest.raises(ValidationError) as exc_info:
        EvidenceCreate(title="合同")  # missing evidence_type
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("evidence_type",) for e in errors)


def test_evidence_create_defaults():
    req = EvidenceCreate(title="劳动合同", evidence_type="contract")
    assert req.description is None
    assert req.sort_order == 0


def test_evidence_create_title_too_long():
    with pytest.raises(ValidationError):
        EvidenceCreate(title="x" * 201, evidence_type="contract")


# ===================================================================
# EvidenceUpdate
# ===================================================================

def test_evidence_update_all_none():
    req = EvidenceUpdate()
    assert req.title is None
    assert req.evidence_type is None
    assert req.sort_order is None


def test_evidence_update_partial():
    req = EvidenceUpdate(title="新标题", sort_order=5)
    assert req.title == "新标题"
    assert req.evidence_type is None
    assert req.sort_order == 5


# ===================================================================
# TimelineCreate
# ===================================================================

def test_timeline_create_requires_event_date():
    with pytest.raises(ValidationError) as exc_info:
        TimelineCreate(event_type="milestone", title="测试事件")  # missing event_date
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("event_date",) for e in errors)


def test_timeline_create_requires_event_type():
    with pytest.raises(ValidationError) as exc_info:
        TimelineCreate(title="测试事件", event_date=date(2026, 5, 15))  # missing event_type
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("event_type",) for e in errors)


def test_timeline_create_requires_title():
    with pytest.raises(ValidationError) as exc_info:
        TimelineCreate(event_type="milestone", event_date=date(2026, 5, 15))  # missing title
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("title",) for e in errors)


def test_timeline_create_valid():
    req = TimelineCreate(
        event_type="milestone",
        title="立案",
        event_date=date(2026, 5, 15),
        description="案件正式立案",
    )
    assert req.event_type == "milestone"
    assert req.event_date == date(2026, 5, 15)
    assert req.description == "案件正式立案"


def test_timeline_create_title_too_long():
    with pytest.raises(ValidationError):
        TimelineCreate(
            event_type="milestone",
            title="x" * 201,
            event_date=date(2026, 5, 15),
        )


# ===================================================================
# TimelineUpdate
# ===================================================================

def test_timeline_update_all_none():
    req = TimelineUpdate()
    assert req.event_type is None
    assert req.title is None
    assert req.description is None
    assert req.event_date is None


def test_timeline_update_partial():
    req = TimelineUpdate(title="新标题", event_date=date(2026, 6, 1))
    assert req.title == "新标题"
    assert req.event_type is None
    assert req.event_date == date(2026, 6, 1)
