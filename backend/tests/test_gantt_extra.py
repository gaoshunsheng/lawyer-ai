"""Extra tests for gantt chart — schemas, resolve_dates, templates, service functions."""

import uuid
from datetime import date, timedelta

import pytest

from app.schemas.gantt import GanttNode, GanttData, GanttDependency, GanttUpdateRequest


# ── GanttNode schema validation ──


def test_gantt_node_missing_id_rejected():
    with pytest.raises(Exception):
        GanttNode(title="test", type="task", start="2026-01-01", end="2026-01-05")


def test_gantt_node_missing_title_rejected():
    with pytest.raises(Exception):
        GanttNode(id="n1", type="task", start="2026-01-01", end="2026-01-05")


def test_gantt_node_missing_type_rejected():
    with pytest.raises(Exception):
        GanttNode(id="n1", title="test", start="2026-01-01", end="2026-01-05")


def test_gantt_node_missing_start_rejected():
    with pytest.raises(Exception):
        GanttNode(id="n1", title="test", type="task", end="2026-01-05")


def test_gantt_node_missing_end_rejected():
    with pytest.raises(Exception):
        GanttNode(id="n1", title="test", type="task", start="2026-01-01")


def test_gantt_node_optional_fields_default():
    node = GanttNode(id="n1", title="test", type="task", start="2026-01-01", end="2026-01-05")
    assert node.assignee_id is None
    assert node.status == "pending"
    assert node.progress == 0
    assert node.description is None


def test_gantt_node_with_all_optional_fields():
    node = GanttNode(
        id="n1", title="举证期限", type="deadline",
        start="2026-01-01", end="2026-01-10",
        assignee_id="user-123",
        status="in_progress",
        progress=60,
        description="准备证据材料",
    )
    assert node.assignee_id == "user-123"
    assert node.status == "in_progress"
    assert node.progress == 60
    assert node.description == "准备证据材料"


def test_gantt_node_progress_zero():
    node = GanttNode(id="n1", title="test", type="task", start="2026-01-01", end="2026-01-05", progress=0)
    assert node.progress == 0


def test_gantt_node_progress_hundred():
    node = GanttNode(id="n1", title="test", type="task", start="2026-01-01", end="2026-01-05", progress=100)
    assert node.progress == 100


def test_gantt_node_progress_negative_rejected():
    with pytest.raises(Exception):
        GanttNode(id="n1", title="test", type="task", start="2026-01-01", end="2026-01-05", progress=-1)


# ── GanttDependency schema ──


def test_gantt_dependency_default_type():
    dep = GanttDependency(**{"from": "n1", "to": "n2"})
    assert dep.type == "finish_to_start"


def test_gantt_dependency_explicit_type():
    dep = GanttDependency(**{"from": "n1", "to": "n2", "type": "start_to_start"})
    assert dep.type == "start_to_start"


def test_gantt_dependency_missing_to_rejected():
    with pytest.raises(Exception):
        GanttDependency(**{"from": "n1"})


# ── GanttData schema ──


def test_gantt_data_with_multiple_nodes():
    data = GanttData(
        nodes=[
            GanttNode(id="n1", title="a", type="task", start="2026-01-01", end="2026-01-05"),
            GanttNode(id="n2", title="b", type="milestone", start="2026-01-05", end="2026-01-06"),
            GanttNode(id="n3", title="c", type="deadline", start="2026-01-06", end="2026-01-10"),
        ],
        dependencies=[
            GanttDependency(**{"from": "n1", "to": "n2"}),
            GanttDependency(**{"from": "n2", "to": "n3"}),
        ],
    )
    assert len(data.nodes) == 3
    assert len(data.dependencies) == 2


def test_gantt_data_nodes_only():
    data = GanttData(
        nodes=[GanttNode(id="n1", title="a", type="task", start="2026-01-01", end="2026-01-05")],
    )
    assert len(data.nodes) == 1
    assert data.dependencies == []


def test_gantt_data_dependencies_only():
    data = GanttData(
        dependencies=[GanttDependency(**{"from": "n1", "to": "n2"})],
    )
    assert data.nodes == []
    assert len(data.dependencies) == 1


# ── GanttUpdateRequest schema ──


def test_gantt_update_request_schema():
    gantt_data = GanttData(
        nodes=[GanttNode(id="n1", title="a", type="task", start="2026-01-01", end="2026-01-05")],
    )
    req = GanttUpdateRequest(gantt_data=gantt_data)
    assert req.gantt_data.nodes[0].id == "n1"


def test_gantt_update_request_empty_data():
    req = GanttUpdateRequest(gantt_data=GanttData())
    assert req.gantt_data.nodes == []
    assert req.gantt_data.dependencies == []


# ── _resolve_dates function ──


def test_resolve_dates_today():
    from app.services.gantt_service import _resolve_dates
    nodes = [GanttNode(id="n1", title="test", type="task", start="today", end="+5d")]
    resolved = _resolve_dates(nodes)
    today = date.today().isoformat()
    assert resolved[0].start == today


def test_resolve_dates_relative_offset():
    from app.services.gantt_service import _resolve_dates
    nodes = [GanttNode(id="n1", title="test", type="task", start="today", end="+10d")]
    resolved = _resolve_dates(nodes)
    expected_end = (date.today() + timedelta(days=10)).isoformat()
    assert resolved[0].end == expected_end


def test_resolve_dates_absolute_dates_unchanged():
    from app.services.gantt_service import _resolve_dates
    nodes = [GanttNode(id="n1", title="test", type="task", start="2026-06-01", end="2026-06-10")]
    resolved = _resolve_dates(nodes)
    assert resolved[0].start == "2026-06-01"
    assert resolved[0].end == "2026-06-10"


def test_resolve_dates_multiple_nodes():
    from app.services.gantt_service import _resolve_dates
    nodes = [
        GanttNode(id="n1", title="a", type="task", start="today", end="+3d"),
        GanttNode(id="n2", title="b", type="task", start="+3d", end="+10d"),
    ]
    resolved = _resolve_dates(nodes)
    assert resolved[0].start != "today"
    assert resolved[1].start != "+3d"
    assert resolved[1].end != "+10d"


# ── Template existence and structure ──


def test_template_count_is_four():
    from app.services.gantt_service import TEMPLATES
    assert len(TEMPLATES) == 4


def test_template_labor_arbitration_node_count():
    from app.services.gantt_service import TEMPLATES
    assert len(TEMPLATES["labor_arbitration"].nodes) == 8


def test_template_first_instance_node_count():
    from app.services.gantt_service import TEMPLATES
    assert len(TEMPLATES["first_instance"].nodes) == 10


def test_template_second_instance_node_count():
    from app.services.gantt_service import TEMPLATES
    assert len(TEMPLATES["second_instance"].nodes) == 7


def test_template_non_litigation_node_count():
    from app.services.gantt_service import TEMPLATES
    assert len(TEMPLATES["non_litigation"].nodes) == 5


def test_template_labor_arbitration_dependency_count():
    from app.services.gantt_service import TEMPLATES
    assert len(TEMPLATES["labor_arbitration"].dependencies) == 6


def test_template_first_instance_dependency_count():
    from app.services.gantt_service import TEMPLATES
    assert len(TEMPLATES["first_instance"].dependencies) == 9


def test_template_second_instance_dependency_count():
    from app.services.gantt_service import TEMPLATES
    assert len(TEMPLATES["second_instance"].dependencies) == 6


def test_template_non_litigation_dependency_count():
    from app.services.gantt_service import TEMPLATES
    assert len(TEMPLATES["non_litigation"].dependencies) == 4


def test_template_node_types_labor_arbitration():
    from app.services.gantt_service import TEMPLATES
    types = {n.type for n in TEMPLATES["labor_arbitration"].nodes}
    assert "task" in types
    assert "milestone" in types
    assert "deadline" in types
    assert "ai_assisted" in types


def test_template_node_types_non_litigation():
    from app.services.gantt_service import TEMPLATES
    types = {n.type for n in TEMPLATES["non_litigation"].nodes}
    assert "task" in types
    assert "milestone" in types
    assert "ai_assisted" in types


# ── Service functions exist ──


def test_gantt_service_functions_callable():
    from app.services.gantt_service import (
        get_gantt,
        update_gantt,
        apply_template,
        _resolve_dates,
    )
    for fn in [get_gantt, update_gantt, apply_template, _resolve_dates]:
        assert callable(fn)
