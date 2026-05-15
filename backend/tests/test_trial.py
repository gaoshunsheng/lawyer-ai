import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.trial import (
    TrialStartRequest,
    TrialRespondRequest,
    TrialSimulationResponse,
    TrialRoundResponse,
)


def test_trial_start_request_validates_mode():
    req = TrialStartRequest(mode="arbitration", role="plaintiff")
    assert req.mode == "arbitration"


def test_trial_start_request_rejects_invalid_mode():
    with pytest.raises(Exception):
        TrialStartRequest(mode="invalid", role="plaintiff")


def test_trial_start_request_rejects_invalid_role():
    with pytest.raises(Exception):
        TrialStartRequest(mode="arbitration", role="invalid")


def test_trial_respond_request_validates_content():
    req = TrialRespondRequest(content="律师论点")
    assert req.content == "律师论点"


def test_trial_respond_request_rejects_empty():
    with pytest.raises(Exception):
        TrialRespondRequest(content="")


@pytest.mark.asyncio
async def test_create_simulation():
    from app.services.trial_service import create_simulation
    db = AsyncMock()
    db.flush = AsyncMock()
    sim = await create_simulation(db, uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), "arbitration", "plaintiff")
    assert sim.mode == "arbitration"
    assert sim.role == "plaintiff"
    assert sim.status == "active"
    assert sim.rounds_completed == 0


@pytest.mark.asyncio
async def test_get_simulation_not_found():
    from app.services.trial_service import get_simulation
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(return_value=mock_result)
    sim = await get_simulation(db, uuid.uuid4())
    assert sim is None


@pytest.mark.asyncio
async def test_add_round():
    from app.services.trial_service import add_round
    db = AsyncMock()
    db.flush = AsyncMock()
    r = await add_round(db, uuid.uuid4(), 1, "ai", "AI质疑内容")
    assert r.round_num == 1
    assert r.role == "ai"
    assert r.content == "AI质疑内容"


@pytest.mark.asyncio
async def test_update_simulation():
    from app.services.trial_service import update_simulation
    from app.models.trial import TrialSimulation
    db = AsyncMock()
    db.flush = AsyncMock()
    sim = TrialSimulation(
        case_id=uuid.uuid4(), tenant_id=uuid.uuid4(), user_id=uuid.uuid4(),
        mode="arbitration", role="plaintiff",
    )
    updated = await update_simulation(db, sim, {"status": "completed", "rounds_completed": 5})
    assert updated.status == "completed"
    assert updated.rounds_completed == 5


@pytest.mark.asyncio
@patch("app.ai.graphs.trial_graph.get_openai_client")
async def test_init_simulation(MockGetClient):
    from app.ai.graphs.trial_graph import init_simulation
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = '{"dispute_focus": ["加班费计算", "经济补偿金", "未签合同双倍工资", "年休假补偿", "社保补缴"]}'
    MockGetClient.return_value.chat.completions.create = AsyncMock(return_value=mock_resp)
    state = await init_simulation({"case_data": {"title": "劳动争议案"}, "mode": "arbitration", "user_role": "plaintiff", "error": ""})
    assert len(state["dispute_focus"]) == 5
    assert "加班费计算" in state["dispute_focus"]


@pytest.mark.asyncio
@patch("app.ai.graphs.trial_graph.get_openai_client")
async def test_ai_attack(MockGetClient):
    from app.ai.graphs.trial_graph import ai_attack
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = "我对你的加班费主张提出质疑，根据考勤记录..."
    MockGetClient.return_value.chat.completions.create = AsyncMock(return_value=mock_resp)
    state = await ai_attack({"mode": "arbitration", "user_role": "plaintiff", "current_round": 1, "user_message": "律师主张", "dispute_focus": ["加班费"], "error": ""})
    assert "质疑" in state["ai_message"]
    assert state["error"] == ""


@pytest.mark.asyncio
@patch("app.ai.graphs.trial_graph.get_openai_client")
async def test_evaluate_argument(MockGetClient):
    from app.ai.graphs.trial_graph import evaluate_argument
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = json.dumps({"strength": "medium", "weaknesses": ["缺少考勤记录"], "score": 55})
    MockGetClient.return_value.chat.completions.create = AsyncMock(return_value=mock_resp)
    state = await evaluate_argument({"user_message": "主张加班费", "dispute_focus": ["加班费"], "ai_message": "质疑", "mode": "arbitration", "user_role": "plaintiff", "error": ""})
    assert state["argument_strength"] == "medium"
    assert state["evaluation"]["score"] == 55


@pytest.mark.asyncio
@patch("app.ai.graphs.trial_graph.get_openai_client")
async def test_generate_strategy_report(MockGetClient):
    from app.ai.graphs.trial_graph import generate_strategy_report
    report = {"dispute_focus": [{"focus": "加班费", "importance": "high"}], "argument_evaluation": [], "risk_points": [], "strategy_suggestions": [], "evidence_suggestions": []}
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = json.dumps(report)
    MockGetClient.return_value.chat.completions.create = AsyncMock(return_value=mock_resp)
    state = await generate_strategy_report({"case_data": {"title": "test"}, "dispute_focus": ["加班费"], "rounds": [], "error": ""})
    assert "strategy_report" in state
    assert state["strategy_report"]["dispute_focus"][0]["focus"] == "加班费"


@pytest.mark.asyncio
@patch("app.ai.graphs.trial_graph.get_openai_client")
async def test_init_simulation_json_error(MockGetClient):
    from app.ai.graphs.trial_graph import init_simulation
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = "not valid json"
    MockGetClient.return_value.chat.completions.create = AsyncMock(return_value=mock_resp)
    state = await init_simulation({"case_data": {"title": "test"}, "mode": "arbitration", "user_role": "plaintiff", "error": ""})
    assert "无效的JSON" in state["error"]


def test_get_opponent_role():
    from app.ai.graphs.trial_graph import _get_opponent_role
    assert _get_opponent_role("arbitration", "plaintiff") == "被申请人代理律师"
    assert _get_opponent_role("arbitration", "defendant") == "申请人代理律师"
    assert _get_opponent_role("first_instance", "plaintiff") == "被告代理律师"
    assert _get_opponent_role("first_instance", "defendant") == "原告代理律师"
    assert _get_opponent_role("judgment", "plaintiff") == "对方律师"
