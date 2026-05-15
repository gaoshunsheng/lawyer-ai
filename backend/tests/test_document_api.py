import pytest
import uuid
from pydantic import ValidationError

from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentGenerateRequest,
    DocumentResponse,
    DocumentListResponse,
    TemplateResponse,
)


# ── DocumentCreate schema tests ──


def test_document_create_requires_title():
    """title is a required field with max_length=200."""
    with pytest.raises(ValidationError) as exc_info:
        DocumentCreate(doc_type="complaint")
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("title",) for e in errors)


def test_document_create_requires_doc_type():
    """doc_type is a required field."""
    with pytest.raises(ValidationError) as exc_info:
        DocumentCreate(title="测试")
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("doc_type",) for e in errors)


def test_document_create_with_all_fields():
    """Should accept all fields including optional ones."""
    template_id = uuid.uuid4()
    case_id = uuid.uuid4()
    variables = {"applicant_name": "张三"}

    req = DocumentCreate(
        title="测试文书",
        doc_type="complaint",
        template_id=template_id,
        case_id=case_id,
        variables=variables,
    )
    assert req.title == "测试文书"
    assert req.doc_type == "complaint"
    assert req.template_id == template_id
    assert req.case_id == case_id
    assert req.variables == variables


def test_document_create_with_only_required_fields():
    """Should accept only title and doc_type."""
    req = DocumentCreate(title="简易文书", doc_type="defense_letter")
    assert req.title == "简易文书"
    assert req.doc_type == "defense_letter"
    assert req.template_id is None
    assert req.case_id is None
    assert req.variables is None


def test_document_create_title_max_length():
    """Title must not exceed 200 characters."""
    with pytest.raises(ValidationError) as exc_info:
        DocumentCreate(title="x" * 201, doc_type="complaint")
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("title",) for e in errors)


def test_document_create_title_at_max_length():
    """Title at exactly 200 characters should be accepted."""
    req = DocumentCreate(title="x" * 200, doc_type="complaint")
    assert len(req.title) == 200


def test_document_create_template_id_must_be_uuid():
    """template_id must be a valid UUID string."""
    with pytest.raises(ValidationError):
        DocumentCreate(title="测试", doc_type="complaint", template_id="not-a-uuid")


def test_document_create_valid_template_id():
    """A valid UUID string for template_id should be accepted."""
    req = DocumentCreate(
        title="测试",
        doc_type="complaint",
        template_id="12345678-1234-1234-1234-123456789012",
    )
    assert req.template_id == uuid.UUID("12345678-1234-1234-1234-123456789012")


# ── DocumentUpdate schema tests ──


def test_document_update_all_optional():
    """All fields in DocumentUpdate are optional."""
    req = DocumentUpdate()
    assert req.title is None
    assert req.content is None
    assert req.variables is None
    assert req.status is None


def test_document_update_with_title_only():
    """Should accept only title."""
    req = DocumentUpdate(title="更新标题")
    assert req.title == "更新标题"
    assert req.content is None


def test_document_update_with_all_fields():
    """Should accept all fields."""
    req = DocumentUpdate(
        title="新标题",
        content={"body": "更新内容"},
        variables={"key": "value"},
        status="published",
    )
    assert req.title == "新标题"
    assert req.content == {"body": "更新内容"}
    assert req.variables == {"key": "value"}
    assert req.status == "published"


# ── DocumentGenerateRequest schema tests ──


def test_generate_request_instructions_optional():
    """instructions field is optional."""
    req = DocumentGenerateRequest()
    assert req.instructions is None


def test_generate_request_with_instructions():
    """Should accept instructions string."""
    req = DocumentGenerateRequest(instructions="请帮我撰写仲裁申请书的事实与理由部分")
    assert req.instructions == "请帮我撰写仲裁申请书的事实与理由部分"


# ── TemplateResponse schema tests ──


def test_template_response_requires_all_fields():
    """TemplateResponse requires id, name, doc_type, content_template,
    variables_schema, category, sort_order, is_system, created_at."""
    with pytest.raises(ValidationError) as exc_info:
        TemplateResponse(name="测试")
    errors = exc_info.value.errors()
    required_fields = {"id", "doc_type", "content_template", "variables_schema", "category", "sort_order", "is_system", "created_at"}
    error_fields = {e["loc"][0] for e in errors}
    assert required_fields.issubset(error_fields)


def test_template_response_from_dict():
    """Should construct from a dict with all required fields."""
    import datetime

    data = {
        "id": uuid.uuid4(),
        "name": "劳动争议仲裁申请书",
        "doc_type": "arbitration_application",
        "content_template": "申请人：{{applicant_name}}",
        "variables_schema": {"variables": []},
        "category": "申请类",
        "sort_order": 1,
        "is_system": True,
        "tenant_id": None,
        "created_at": datetime.datetime.now(),
    }
    resp = TemplateResponse(**data)
    assert resp.name == "劳动争议仲裁申请书"
    assert resp.is_system is True


# ── DocumentListResponse schema tests ──


def test_document_list_response_empty():
    """Should accept empty items list."""
    resp = DocumentListResponse(items=[], total=0, page=1, page_size=20)
    assert resp.items == []
    assert resp.total == 0
    assert resp.page == 1
    assert resp.page_size == 20


def test_document_list_response_with_items():
    """Should validate items as DocumentResponse objects."""
    import datetime

    doc_data = {
        "id": uuid.uuid4(),
        "case_id": None,
        "tenant_id": uuid.uuid4(),
        "user_id": uuid.uuid4(),
        "title": "测试文书",
        "doc_type": "complaint",
        "template_id": None,
        "content": None,
        "variables": None,
        "status": "draft",
        "version": 1,
        "parent_id": None,
        "created_at": datetime.datetime.now(),
        "updated_at": datetime.datetime.now(),
    }
    resp = DocumentListResponse(items=[doc_data], total=1, page=1, page_size=20)
    assert len(resp.items) == 1
    assert resp.items[0].title == "测试文书"
