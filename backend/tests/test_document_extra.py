"""Extra tests for document enhancement — schemas, diff logic, service functions, edge cases."""

import difflib
import uuid

import pytest

from app.schemas.document import (
    BatchGenerateRequest,
    DocumentResponse,
    DocumentCreate,
    DocumentUpdate,
    DocumentListResponse,
    VersionDiffResponse,
)


# ── BatchGenerateRequest validation ──


def test_batch_generate_request_valid():
    req = BatchGenerateRequest(
        template_id=uuid.uuid4(),
        variable_sets=[{"name": "张三"}, {"name": "李四"}, {"name": "王五"}],
    )
    assert len(req.variable_sets) == 3


def test_batch_generate_request_single_item():
    req = BatchGenerateRequest(
        template_id=uuid.uuid4(),
        variable_sets=[{"key": "value"}],
    )
    assert len(req.variable_sets) == 1


def test_batch_generate_request_max_items():
    req = BatchGenerateRequest(
        template_id=uuid.uuid4(),
        variable_sets=[{"k": f"v{i}"} for i in range(20)],
    )
    assert len(req.variable_sets) == 20


def test_batch_generate_request_21_items_rejected():
    with pytest.raises(Exception):
        BatchGenerateRequest(
            template_id=uuid.uuid4(),
            variable_sets=[{"k": f"v{i}"} for i in range(21)],
        )


def test_batch_generate_request_empty_rejected():
    with pytest.raises(Exception):
        BatchGenerateRequest(
            template_id=uuid.uuid4(),
            variable_sets=[],
        )


# ── VersionDiffResponse schema ──


def test_version_diff_response_schema():
    resp = VersionDiffResponse(
        old_version=1,
        new_version=3,
        diffs=[
            {"type": "added", "content": "新条款"},
            {"type": "removed", "content": "旧条款"},
        ],
    )
    assert resp.old_version == 1
    assert resp.new_version == 3
    assert len(resp.diffs) == 2


def test_version_diff_response_empty_diffs():
    resp = VersionDiffResponse(old_version=2, new_version=2, diffs=[])
    assert resp.diffs == []


def test_version_diff_response_many_diffs():
    diffs = [{"type": "added", "content": f"line{i}"} for i in range(50)]
    resp = VersionDiffResponse(old_version=1, new_version=5, diffs=diffs)
    assert len(resp.diffs) == 50


# ── DocumentResponse with parent_id ──


def test_document_response_with_parent_id():
    parent = uuid.uuid4()
    resp = DocumentResponse(
        id=uuid.uuid4(), case_id=None, tenant_id=uuid.uuid4(), user_id=uuid.uuid4(),
        title="测试文档", doc_type="complaint", template_id=None,
        content={"raw": "内容"}, variables=None, status="draft",
        version=3, parent_id=parent,
        created_at="2026-01-01T00:00:00", updated_at="2026-01-01T00:00:00",
    )
    assert resp.parent_id == parent
    assert resp.version == 3


def test_document_response_no_parent():
    resp = DocumentResponse(
        id=uuid.uuid4(), case_id=None, tenant_id=uuid.uuid4(), user_id=uuid.uuid4(),
        title="原始文档", doc_type="complaint", template_id=None,
        content={"raw": "内容"}, variables=None, status="draft",
        version=1, parent_id=None,
        created_at="2026-01-01T00:00:00", updated_at="2026-01-01T00:00:00",
    )
    assert resp.parent_id is None
    assert resp.version == 1


# ── DocumentCreate schema ──


def test_document_create_with_all_fields():
    req = DocumentCreate(
        title="劳动仲裁申请书",
        doc_type="arbitration_application",
        template_id=uuid.uuid4(),
        case_id=uuid.uuid4(),
        variables={"applicant_name": "张三"},
    )
    assert req.title == "劳动仲裁申请书"
    assert req.variables["applicant_name"] == "张三"


def test_document_create_minimal():
    req = DocumentCreate(title="新文档", doc_type="other")
    assert req.template_id is None
    assert req.case_id is None
    assert req.variables is None


def test_document_create_title_max_length():
    long_title = "A" * 200
    req = DocumentCreate(title=long_title, doc_type="test")
    assert len(req.title) == 200


def test_document_create_title_over_max_rejected():
    with pytest.raises(Exception):
        DocumentCreate(title="A" * 201, doc_type="test")


# ── DocumentUpdate schema ──


def test_document_update_all_none():
    req = DocumentUpdate()
    assert req.title is None
    assert req.content is None
    assert req.variables is None
    assert req.status is None


def test_document_update_partial():
    req = DocumentUpdate(status="approved", title="更新标题")
    assert req.status == "approved"
    assert req.title == "更新标题"
    assert req.content is None


# ── DocumentListResponse schema ──


def test_document_list_response():
    resp = DocumentListResponse(items=[], total=0, page=1, page_size=20)
    assert resp.items == []
    assert resp.total == 0


# ── Diff logic using difflib directly ──


def test_diff_empty_content_vs_content():
    old_lines = []
    new_lines = ["第一行", "第二行"]
    diff = list(difflib.unified_diff(old_lines, new_lines, lineterm=""))
    added = [l for l in diff if l.startswith("+") and not l.startswith("+++")]
    assert len(added) == 2


def test_diff_content_vs_empty():
    old_lines = ["第一行", "第二行"]
    new_lines = []
    diff = list(difflib.unified_diff(old_lines, new_lines, lineterm=""))
    removed = [l for l in diff if l.startswith("-") and not l.startswith("---")]
    assert len(removed) == 2


def test_diff_identical_content():
    lines = ["第一行", "第二行", "第三行"]
    diff = list(difflib.unified_diff(lines, lines, lineterm=""))
    added = [l for l in diff if l.startswith("+") and not l.startswith("+++")]
    removed = [l for l in diff if l.startswith("-") and not l.startswith("---")]
    assert added == []
    assert removed == []


def test_diff_single_line_change():
    old = ["甲方：张三"]
    new = ["甲方：李四"]
    diff = list(difflib.unified_diff(old, new, lineterm=""))
    removed = [l for l in diff if l.startswith("-") and not l.startswith("---")]
    added = [l for l in diff if l.startswith("+") and not l.startswith("+++")]
    assert any("张三" in l for l in removed)
    assert any("李四" in l for l in added)


def test_diff_multiline_changes():
    old = ["第一条", "第二条", "第三条"]
    new = ["第一条", "修改的第二条", "第三条", "新增第四条"]
    diff = list(difflib.unified_diff(old, new, lineterm=""))
    added = [l for l in diff if l.startswith("+") and not l.startswith("+++")]
    removed = [l for l in diff if l.startswith("-") and not l.startswith("---")]
    assert len(added) >= 1
    assert len(removed) >= 1


# ── Document service functions exist ──


def test_document_service_version_functions():
    from app.services.document_service import list_versions, diff_versions, rollback_version
    assert callable(list_versions)
    assert callable(diff_versions)
    assert callable(rollback_version)


def test_document_service_crud_functions():
    from app.services.document_service import (
        create_document,
        get_document,
        update_document,
        list_documents,
        create_version,
    )
    for fn in [create_document, get_document, update_document, list_documents, create_version]:
        assert callable(fn)


def test_document_service_template_functions():
    from app.services.document_service import (
        seed_templates,
        list_templates,
        get_template,
    )
    for fn in [seed_templates, list_templates, get_template]:
        assert callable(fn)
