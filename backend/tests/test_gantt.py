import pytest
from app.schemas.gantt import GanttNode, GanttData, GanttDependency


def test_gantt_node_validates_type():
    node = GanttNode(id="n1", title="test", type="milestone", start="2026-01-01", end="2026-01-05")
    assert node.type == "milestone"


def test_gantt_node_validates_all_types():
    for t in ("deadline", "milestone", "task", "ai_assisted"):
        node = GanttNode(id="n1", title="test", type=t, start="2026-01-01", end="2026-01-05")
        assert node.type == t


def test_gantt_node_rejects_invalid_type():
    with pytest.raises(Exception):
        GanttNode(id="n1", title="test", type="invalid", start="2026-01-01", end="2026-01-05")


def test_gantt_node_validates_status():
    node = GanttNode(id="n1", title="test", type="task", start="2026-01-01", end="2026-01-05", status="in_progress")
    assert node.status == "in_progress"


def test_gantt_node_rejects_invalid_status():
    with pytest.raises(Exception):
        GanttNode(id="n1", title="test", type="task", start="2026-01-01", end="2026-01-05", status="unknown")


def test_gantt_node_progress_range():
    with pytest.raises(Exception):
        GanttNode(id="n1", title="test", type="task", start="2026-01-01", end="2026-01-05", progress=150)


def test_gantt_dependency_from_alias():
    dep = GanttDependency(**{"from": "n1", "to": "n2"})
    assert dep.from_ == "n1"
    assert dep.to == "n2"


def test_gantt_data_model():
    data = GanttData(
        nodes=[GanttNode(id="n1", title="a", type="task", start="2026-01-01", end="2026-01-05")],
        dependencies=[GanttDependency(**{"from": "n1", "to": "n2"})],
    )
    assert len(data.nodes) == 1
    assert len(data.dependencies) == 1


def test_gantt_data_empty():
    data = GanttData()
    assert data.nodes == []
    assert data.dependencies == []


def test_template_exists_all_types():
    from app.services.gantt_service import TEMPLATES
    assert "labor_arbitration" in TEMPLATES
    assert "first_instance" in TEMPLATES
    assert "second_instance" in TEMPLATES
    assert "non_litigation" in TEMPLATES


def test_template_labor_arbitration():
    from app.services.gantt_service import TEMPLATES
    t = TEMPLATES["labor_arbitration"]
    assert len(t.nodes) == 8
    assert len(t.dependencies) == 6


def test_template_first_instance():
    from app.services.gantt_service import TEMPLATES
    t = TEMPLATES["first_instance"]
    assert len(t.nodes) == 10
    assert len(t.dependencies) == 9


def test_template_second_instance():
    from app.services.gantt_service import TEMPLATES
    t = TEMPLATES["second_instance"]
    assert len(t.nodes) == 7
    assert len(t.dependencies) == 6


def test_template_non_litigation():
    from app.services.gantt_service import TEMPLATES
    t = TEMPLATES["non_litigation"]
    assert len(t.nodes) == 5
    assert len(t.dependencies) == 4


def test_resolve_dates():
    from app.services.gantt_service import _resolve_dates
    nodes = [GanttNode(id="n1", title="test", type="task", start="today", end="+5d")]
    resolved = _resolve_dates(nodes)
    assert resolved[0].start != "today"
    assert resolved[0].end != "+5d"


def test_template_node_types_covered():
    from app.services.gantt_service import TEMPLATES
    all_types = set()
    for t in TEMPLATES.values():
        for n in t.nodes:
            all_types.add(n.type)
    assert "deadline" in all_types
    assert "milestone" in all_types
    assert "task" in all_types
    assert "ai_assisted" in all_types
