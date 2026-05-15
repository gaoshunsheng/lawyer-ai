"""Unit tests for app/services/case_service.py

All database interactions are mocked via unittest.mock.AsyncMock.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services import case_service


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_scalar_result(value):
    """Return a MagicMock whose .scalar() returns *value*."""
    mock_result = MagicMock()
    mock_result.scalar.return_value = value
    return mock_result


def _mock_scalars_all_result(items: list):
    """Return a MagicMock whose .scalars().all() returns *items*."""
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = items
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    return mock_result


def _make_case(**overrides):
    """Build a lightweight Case-like object for testing update_case etc."""
    defaults = dict(
        id=uuid.uuid4(),
        case_number="LD-2026-0001",
        title="Test case",
        case_type="labor_contract",
        status="pending",
        plaintiff={},
        defendant={},
        claim_amount=None,
        dispute_focus=None,
        lawyer_id=uuid.uuid4(),
        assistant_id=None,
        tenant_id=uuid.uuid4(),
        gantt_data=None,
        ai_analysis=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    defaults.update(overrides)

    case = MagicMock()
    for k, v in defaults.items():
        setattr(case, k, v)
    return case


# ===================================================================
# generate_case_number
# ===================================================================

@pytest.mark.asyncio
async def test_generate_case_number_format():
    mock_db = AsyncMock()
    # count query returns 5 existing cases
    mock_db.execute.return_value = _mock_scalar_result(5)

    tenant_id = uuid.uuid4()
    result = await case_service.generate_case_number(mock_db, tenant_id)

    year = datetime.now().year
    assert result == f"LD-{year}-0006"


@pytest.mark.asyncio
async def test_generate_case_number_first_case():
    mock_db = AsyncMock()
    # count query returns None (no cases yet)
    mock_db.execute.return_value = _mock_scalar_result(None)

    result = await case_service.generate_case_number(mock_db, uuid.uuid4())
    year = datetime.now().year
    assert result == f"LD-{year}-0001"


@pytest.mark.asyncio
async def test_generate_case_number_zero_count():
    mock_db = AsyncMock()
    mock_db.execute.return_value = _mock_scalar_result(0)

    result = await case_service.generate_case_number(mock_db, uuid.uuid4())
    year = datetime.now().year
    assert result == f"LD-{year}-0001"


# ===================================================================
# list_cases
# ===================================================================

@pytest.mark.asyncio
async def test_list_cases_basic():
    mock_db = AsyncMock()
    cases = [_make_case(title=f"Case {i}") for i in range(3)]

    # First call: count query. Second call: select query.
    mock_db.execute.side_effect = [
        _mock_scalar_result(3),           # total count
        _mock_scalars_all_result(cases),   # items
    ]

    tenant_id = uuid.uuid4()
    items, total = await case_service.list_cases(mock_db, tenant_id, page=1, page_size=20)

    assert total == 3
    assert len(items) == 3


@pytest.mark.asyncio
async def test_list_cases_with_status_filter():
    mock_db = AsyncMock()
    mock_db.execute.side_effect = [
        _mock_scalar_result(1),
        _mock_scalars_all_result([_make_case(status="active")]),
    ]

    items, total = await case_service.list_cases(
        mock_db, uuid.uuid4(), status="active"
    )
    assert total == 1
    assert items[0].status == "active"


@pytest.mark.asyncio
async def test_list_cases_with_search():
    mock_db = AsyncMock()
    mock_db.execute.side_effect = [
        _mock_scalar_result(1),
        _mock_scalars_all_result([_make_case(title="工资纠纷")]),
    ]

    items, total = await case_service.list_cases(
        mock_db, uuid.uuid4(), search="工资"
    )
    assert total == 1


@pytest.mark.asyncio
async def test_list_cases_pagination():
    mock_db = AsyncMock()
    # Page 2, page_size 5 => offset = 5
    mock_db.execute.side_effect = [
        _mock_scalar_result(12),
        _mock_scalars_all_result([_make_case() for _ in range(5)]),
    ]

    items, total = await case_service.list_cases(
        mock_db, uuid.uuid4(), page=2, page_size=5
    )
    assert total == 12
    assert len(items) == 5


@pytest.mark.asyncio
async def test_list_cases_empty():
    mock_db = AsyncMock()
    mock_db.execute.side_effect = [
        _mock_scalar_result(0),
        _mock_scalars_all_result([]),
    ]

    items, total = await case_service.list_cases(mock_db, uuid.uuid4())
    assert total == 0
    assert items == []


# ===================================================================
# get_case
# ===================================================================

@pytest.mark.asyncio
async def test_get_case_found():
    mock_db = AsyncMock()
    case = _make_case()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = case
    mock_db.execute.return_value = mock_result

    result = await case_service.get_case(mock_db, case.id)
    assert result is case


@pytest.mark.asyncio
async def test_get_case_not_found():
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    result = await case_service.get_case(mock_db, uuid.uuid4())
    assert result is None


# ===================================================================
# create_case
# ===================================================================

@pytest.mark.asyncio
async def test_create_case():
    mock_db = AsyncMock()
    # generate_case_number will call db.execute
    mock_db.execute.return_value = _mock_scalar_result(0)

    tenant_id = uuid.uuid4()
    lawyer_id = uuid.uuid4()
    data = {
        "title": "New case",
        "case_type": "labor_contract",
        "plaintiff": {"name": "张三"},
        "defendant": {"name": "李四"},
    }

    mock_db.add = MagicMock()  # db.add is sync, not async
    with patch.object(case_service, "generate_case_number", return_value="LD-2026-0001"):
        result = await case_service.create_case(mock_db, tenant_id, lawyer_id, data)

    mock_db.add.assert_called_once()
    mock_db.flush.assert_awaited_once()


# ===================================================================
# update_case
# ===================================================================

@pytest.mark.asyncio
async def test_update_case_sets_non_none_fields():
    mock_db = AsyncMock()
    case = _make_case(title="Old title", status="pending")

    result = await case_service.update_case(mock_db, case, {
        "title": "New title",
        "status": None,  # should be skipped
    })

    assert result.title == "New title"
    assert result.status == "pending"  # unchanged
    mock_db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_case_all_none_data():
    mock_db = AsyncMock()
    case = _make_case(title="Original")

    result = await case_service.update_case(mock_db, case, {
        "title": None,
        "status": None,
    })

    assert result.title == "Original"
    mock_db.flush.assert_awaited_once()


# ===================================================================
# update_case_status
# ===================================================================

@pytest.mark.asyncio
async def test_update_case_status():
    mock_db = AsyncMock()
    case = _make_case(status="pending")

    result = await case_service.update_case_status(mock_db, case, "active")
    assert result.status == "active"
    mock_db.flush.assert_awaited_once()


# ===================================================================
# Evidence CRUD
# ===================================================================

@pytest.mark.asyncio
async def test_list_evidences():
    mock_db = AsyncMock()
    case_id = uuid.uuid4()
    ev1 = MagicMock()
    ev1.title = "Contract"
    ev2 = MagicMock()
    ev2.title = "Photo"

    mock_db.execute.return_value = _mock_scalars_all_result([ev1, ev2])

    result = await case_service.list_evidences(mock_db, case_id)
    assert len(result) == 2


@pytest.mark.asyncio
async def test_list_evidences_empty():
    mock_db = AsyncMock()
    mock_db.execute.return_value = _mock_scalars_all_result([])

    result = await case_service.list_evidences(mock_db, uuid.uuid4())
    assert result == []


@pytest.mark.asyncio
async def test_create_evidence():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()  # db.add is sync, not async
    case_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    data = {"title": "合同原件", "evidence_type": "contract", "description": "原件扫描件"}

    result = await case_service.create_evidence(
        mock_db, case_id, tenant_id, data,
        file_url="/uploads/contract.pdf", file_size=1024, file_type="application/pdf",
    )

    mock_db.add.assert_called_once()
    mock_db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_evidence():
    mock_db = AsyncMock()
    evidence = MagicMock()

    await case_service.delete_evidence(mock_db, evidence)
    mock_db.delete.assert_awaited_once_with(evidence)
    mock_db.flush.assert_awaited_once()


# ===================================================================
# Timeline CRUD
# ===================================================================

@pytest.mark.asyncio
async def test_list_timelines():
    mock_db = AsyncMock()
    case_id = uuid.uuid4()
    t1 = MagicMock()
    t1.title = "立案"
    t2 = MagicMock()
    t2.title = "开庭"

    mock_db.execute.return_value = _mock_scalars_all_result([t1, t2])

    result = await case_service.list_timelines(mock_db, case_id)
    assert len(result) == 2


@pytest.mark.asyncio
async def test_list_timelines_empty():
    mock_db = AsyncMock()
    mock_db.execute.return_value = _mock_scalars_all_result([])

    result = await case_service.list_timelines(mock_db, uuid.uuid4())
    assert result == []


@pytest.mark.asyncio
async def test_create_timeline():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()  # db.add is sync, not async
    case_id = uuid.uuid4()
    created_by = uuid.uuid4()
    data = {
        "event_type": "milestone",
        "title": "立案",
        "description": "案件正式立案",
        "event_date": date(2026, 5, 15),
    }

    result = await case_service.create_timeline(mock_db, case_id, created_by, data)
    mock_db.add.assert_called_once()
    mock_db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_timeline():
    mock_db = AsyncMock()
    timeline = MagicMock()

    await case_service.delete_timeline(mock_db, timeline)
    mock_db.delete.assert_awaited_once_with(timeline)
    mock_db.flush.assert_awaited_once()
