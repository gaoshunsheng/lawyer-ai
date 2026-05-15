import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock

from app.services import feedback_service


# ── Stats tests ──

@pytest.mark.asyncio
async def test_get_stats_empty():
    mock_db = AsyncMock()
    count_result = MagicMock()
    count_result.scalar.return_value = 0
    mock_db.execute.return_value = count_result

    stats = await feedback_service.get_feedback_stats(mock_db, uuid.uuid4())
    assert stats["total"] == 0
    assert stats["positive_rate"] == 0
    assert stats["negative_rate"] == 0
    assert stats["avg_law_accuracy"] == 0
    assert stats["avg_analysis_depth"] == 0
    assert stats["avg_practical_value"] == 0


@pytest.mark.asyncio
async def test_get_stats_with_data():
    mock_db = AsyncMock()
    tenant_id = uuid.uuid4()

    # Mock count queries
    count_result = MagicMock()
    count_result.scalar.return_value = 10
    # Mock positive count
    pos_result = MagicMock()
    pos_result.scalar.return_value = 8
    # Mock avg queries
    avg_row = MagicMock()
    avg_row.avg_law = 4.0
    avg_row.avg_depth = 3.5
    avg_row.avg_value = 4.5
    avg_result = MagicMock()
    avg_result.one.return_value = avg_row

    # First call returns total count, second returns positive count, third returns avgs
    mock_db.execute.side_effect = [count_result, pos_result, avg_result]

    stats = await feedback_service.get_feedback_stats(mock_db, tenant_id)
    assert stats["total"] == 10
    assert stats["positive_rate"] == 80.0
    assert stats["negative_rate"] == 20.0
    assert stats["avg_law_accuracy"] == 4.0
    assert stats["avg_analysis_depth"] == 3.5
    assert stats["avg_practical_value"] == 4.5


@pytest.mark.asyncio
async def test_get_stats_all_positive():
    mock_db = AsyncMock()

    count_result = MagicMock()
    count_result.scalar.return_value = 5
    pos_result = MagicMock()
    pos_result.scalar.return_value = 5
    avg_row = MagicMock()
    avg_row.avg_law = 5.0
    avg_row.avg_depth = 5.0
    avg_row.avg_value = 5.0
    avg_result = MagicMock()
    avg_result.one.return_value = avg_row

    mock_db.execute.side_effect = [count_result, pos_result, avg_result]

    stats = await feedback_service.get_feedback_stats(mock_db, uuid.uuid4())
    assert stats["positive_rate"] == 100.0
    assert stats["negative_rate"] == 0.0


@pytest.mark.asyncio
async def test_get_stats_none_avg_returns_zero():
    mock_db = AsyncMock()

    count_result = MagicMock()
    count_result.scalar.return_value = 3
    pos_result = MagicMock()
    pos_result.scalar.return_value = 1
    avg_row = MagicMock()
    avg_row.avg_law = None
    avg_row.avg_depth = None
    avg_row.avg_value = None
    avg_result = MagicMock()
    avg_result.one.return_value = avg_row

    mock_db.execute.side_effect = [count_result, pos_result, avg_result]

    stats = await feedback_service.get_feedback_stats(mock_db, uuid.uuid4())
    assert stats["avg_law_accuracy"] == 0
    assert stats["avg_analysis_depth"] == 0
    assert stats["avg_practical_value"] == 0


# ── Trends tests ──

@pytest.mark.asyncio
async def test_get_trends_empty():
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.all.return_value = []
    mock_db.execute.return_value = mock_result

    trends = await feedback_service.get_feedback_trends(mock_db, uuid.uuid4())
    assert trends == []


@pytest.mark.asyncio
async def test_get_trends_with_data():
    mock_db = AsyncMock()

    # Mock a row with period, total, positive
    mock_row = MagicMock()
    mock_row.period = "2026-05-14"
    mock_row.total = 5
    mock_row.positive = 4

    mock_result = MagicMock()
    mock_result.all.return_value = [mock_row]
    mock_db.execute.return_value = mock_result

    trends = await feedback_service.get_feedback_trends(mock_db, uuid.uuid4())
    assert len(trends) == 1
    assert trends[0]["total"] == 5
    assert trends[0]["positive"] == 4
    assert trends[0]["negative"] == 1
    assert trends[0]["satisfaction_rate"] == 80.0


@pytest.mark.asyncio
async def test_get_trends_multiple_periods():
    mock_db = AsyncMock()

    row1 = MagicMock()
    row1.period = "2026-05-13"
    row1.total = 10
    row1.positive = 9

    row2 = MagicMock()
    row2.period = "2026-05-14"
    row2.total = 8
    row2.positive = 6

    mock_result = MagicMock()
    mock_result.all.return_value = [row1, row2]
    mock_db.execute.return_value = mock_result

    trends = await feedback_service.get_feedback_trends(mock_db, uuid.uuid4())
    assert len(trends) == 2
    assert trends[0]["satisfaction_rate"] == 90.0
    assert trends[1]["satisfaction_rate"] == 75.0


@pytest.mark.asyncio
async def test_get_trends_zero_positive():
    mock_db = AsyncMock()

    mock_row = MagicMock()
    mock_row.period = "2026-05-14"
    mock_row.total = 3
    mock_row.positive = 0

    mock_result = MagicMock()
    mock_result.all.return_value = [mock_row]
    mock_db.execute.return_value = mock_result

    trends = await feedback_service.get_feedback_trends(mock_db, uuid.uuid4())
    assert len(trends) == 1
    assert trends[0]["positive"] == 0
    assert trends[0]["negative"] == 3
    assert trends[0]["satisfaction_rate"] == 0.0
