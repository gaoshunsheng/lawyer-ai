import difflib
import uuid

import pytest

from app.schemas.document import (
    BatchGenerateRequest,
    DocumentResponse,
    VersionDiffResponse,
)


# --- Version Diff Logic ---

def test_diff_basic():
    old = ["第一行", "第二行", "第三行"]
    new = ["第一行", "修改行", "第三行", "第四行"]
    diff = list(difflib.unified_diff(old, new, lineterm=""))
    assert any("修改行" in d for d in diff)
    assert any("第四行" in d for d in diff)


def test_diff_no_change():
    lines = ["第一行", "第二行"]
    diff = list(difflib.unified_diff(lines, lines, lineterm=""))
    # unified_diff returns only header when no changes
    added = [l for l in diff if l.startswith("+") and not l.startswith("+++")]
    removed = [l for l in diff if l.startswith("-") and not l.startswith("---")]
    assert added == []
    assert removed == []


def test_diff_all_removed():
    old = ["a", "b", "c"]
    new = []
    diff = list(difflib.unified_diff(old, new, lineterm=""))
    removed = [l for l in diff if l.startswith("-") and not l.startswith("---")]
    assert len(removed) == 3


def test_diff_all_added():
    old = []
    new = ["x", "y", "z"]
    diff = list(difflib.unified_diff(old, new, lineterm=""))
    added = [l for l in diff if l.startswith("+") and not l.startswith("+++")]
    assert len(added) == 3


def test_diff_with_chinese():
    old = ["甲方：张三", "乙方：李四"]
    new = ["甲方：王五", "乙方：李四", "丙方：赵六"]
    diff = list(difflib.unified_diff(old, new, lineterm=""))
    assert any("王五" in l for l in diff)
    assert any("赵六" in l for l in diff)


# --- Schema Tests ---

def test_batch_generate_request():
    tid = uuid.uuid4()
    req = BatchGenerateRequest(
        template_id=tid,
        variable_sets=[{"name": "张三"}, {"name": "李四"}],
    )
    assert req.template_id == tid
    assert len(req.variable_sets) == 2


def test_batch_generate_request_single():
    req = BatchGenerateRequest(
        template_id=uuid.uuid4(),
        variable_sets=[{"key": "value"}],
    )
    assert len(req.variable_sets) == 1


def test_batch_generate_request_too_many():
    with pytest.raises(Exception):
        BatchGenerateRequest(
            template_id=uuid.uuid4(),
            variable_sets=[{"k": "v"}] * 21,
        )


def test_batch_generate_request_empty():
    with pytest.raises(Exception):
        BatchGenerateRequest(
            template_id=uuid.uuid4(),
            variable_sets=[],
        )


def test_version_diff_response():
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
    assert resp.diffs[0]["type"] == "added"


def test_document_response_schema():
    import datetime
    resp = DocumentResponse(
        id=uuid.uuid4(),
        case_id=None,
        tenant_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        title="仲裁申请书",
        doc_type="arbitration_application",
        template_id=None,
        content={"raw": "测试内容"},
        variables=None,
        status="draft",
        version=2,
        parent_id=uuid.uuid4(),
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )
    assert resp.version == 2
    assert resp.parent_id is not None


# --- Document Service Functions ---

def test_document_service_has_version_functions():
    from app.services.document_service import (
        list_versions,
        diff_versions,
        rollback_version,
    )
    assert callable(list_versions)
    assert callable(diff_versions)
    assert callable(rollback_version)


def test_document_service_diff_logic():
    """Test the diff logic used in diff_versions without DB."""
    old_text = "甲方：张三\n乙方：李四"
    new_text = "甲方：王五\n乙方：李四\n丙方：赵六"
    diff_lines = list(difflib.unified_diff(old_text.splitlines(), new_text.splitlines(), lineterm=""))
    diffs = []
    for line in diff_lines:
        if line.startswith("+") and not line.startswith("+++"):
            diffs.append({"type": "added", "content": line[1:]})
        elif line.startswith("-") and not line.startswith("---"):
            diffs.append({"type": "removed", "content": line[1:]})
    assert any(d["content"] == "甲方：王五" for d in diffs)
    assert any(d["content"] == "丙方：赵六" for d in diffs)
    assert any(d["content"] == "甲方：张三" for d in diffs)
