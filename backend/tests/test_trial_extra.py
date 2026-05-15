"""Extra tests for trial simulation — models, schemas, prompts, graph, service functions."""

import datetime
import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.trial import TrialSimulation, TrialRound
from app.schemas.trial import (
    TrialStartRequest,
    TrialRespondRequest,
    TrialSimulationResponse,
    TrialRoundResponse,
    StrategyReportResponse,
)


# ── Model construction ──


def test_trial_simulation_model_construction():
    case_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    sim = TrialSimulation(
        case_id=case_id,
        tenant_id=tenant_id,
        user_id=user_id,
        mode="arbitration",
        role="plaintiff",
        status="active",
        rounds_completed=0,
    )
    assert sim.case_id == case_id
    assert sim.tenant_id == tenant_id
    assert sim.user_id == user_id
    assert sim.mode == "arbitration"
    assert sim.role == "plaintiff"
    assert sim.status == "active"
    assert sim.rounds_completed == 0


def test_trial_simulation_model_all_modes():
    for mode in ("arbitration", "first_instance", "defense", "judgment"):
        sim = TrialSimulation(
            case_id=uuid.uuid4(), tenant_id=uuid.uuid4(), user_id=uuid.uuid4(),
            mode=mode, role="plaintiff",
        )
        assert sim.mode == mode


def test_trial_simulation_model_optional_fields():
    sim = TrialSimulation(
        case_id=uuid.uuid4(), tenant_id=uuid.uuid4(), user_id=uuid.uuid4(),
        mode="arbitration", role="defendant",
        dispute_focus={"points": ["加班费"]},
        strategy_report={"summary": "test"},
    )
    assert sim.dispute_focus == {"points": ["加班费"]}
    assert sim.strategy_report == {"summary": "test"}


def test_trial_round_model_construction():
    sim_id = uuid.uuid4()
    r = TrialRound(
        simulation_id=sim_id,
        round_num=1,
        role="plaintiff",
        content="律师主张加班费",
    )
    assert r.simulation_id == sim_id
    assert r.round_num == 1
    assert r.role == "plaintiff"
    assert r.content == "律师主张加班费"
    assert r.argument_strength is None
    assert r.evaluation is None


def test_trial_round_model_with_evaluation():
    r = TrialRound(
        simulation_id=uuid.uuid4(),
        round_num=2,
        role="ai",
        content="AI质疑",
        argument_strength="medium",
        evaluation={"score": 55, "weaknesses": ["缺少证据"]},
    )
    assert r.argument_strength == "medium"
    assert r.evaluation["score"] == 55


# ── Schema validation ──


def test_trial_start_request_all_valid_modes():
    for mode in ("arbitration", "first_instance", "defense", "judgment"):
        req = TrialStartRequest(mode=mode, role="plaintiff")
        assert req.mode == mode


def test_trial_start_request_all_valid_roles():
    for role in ("plaintiff", "defendant", "judge"):
        req = TrialStartRequest(mode="arbitration", role=role)
        assert req.role == role


def test_trial_start_request_empty_mode_rejected():
    with pytest.raises(Exception):
        TrialStartRequest(mode="", role="plaintiff")


def test_trial_start_request_empty_role_rejected():
    with pytest.raises(Exception):
        TrialStartRequest(mode="arbitration", role="")


def test_trial_respond_request_accepts_max_length():
    content = "A" * 5000
    req = TrialRespondRequest(content=content)
    assert len(req.content) == 5000


def test_trial_respond_request_rejects_over_max():
    with pytest.raises(Exception):
        TrialRespondRequest(content="A" * 5001)


def test_trial_simulation_response_schema():
    now = datetime.datetime.now()
    resp = TrialSimulationResponse(
        id=uuid.uuid4(),
        case_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        mode="first_instance",
        role="defendant",
        status="active",
        rounds_completed=3,
        dispute_focus=["加班费"],
        strategy_report=None,
        created_at=now,
        updated_at=now,
    )
    assert resp.rounds_completed == 3
    assert resp.dispute_focus == ["加班费"]
    assert resp.strategy_report is None


def test_trial_round_response_schema():
    now = datetime.datetime.now()
    resp = TrialRoundResponse(
        id=uuid.uuid4(),
        simulation_id=uuid.uuid4(),
        round_num=1,
        role="ai",
        content="AI质疑内容",
        argument_strength="strong",
        evaluation={"score": 80},
        created_at=now,
    )
    assert resp.round_num == 1
    assert resp.argument_strength == "strong"
    assert resp.evaluation["score"] == 80


def test_strategy_report_response_schema():
    resp = StrategyReportResponse(
        dispute_focus=[{"focus": "加班费", "importance": "high"}],
        argument_evaluation=[{"argument": "加班费主张", "strength": "strong", "score": 85}],
        risk_points=[{"risk": "证据不足", "level": "medium", "mitigation": "补充考勤记录"}],
        strategy_suggestions=[{"strategy": "强化证据链", "priority": "high"}],
        evidence_suggestions=[{"gap": "缺少考勤表", "recommended_action": "申请法院调取"}],
    )
    assert len(resp.dispute_focus) == 1
    assert len(resp.argument_evaluation) == 1
    assert len(resp.risk_points) == 1
    assert len(resp.strategy_suggestions) == 1
    assert len(resp.evidence_suggestions) == 1


def test_strategy_report_response_empty_lists():
    resp = StrategyReportResponse(
        dispute_focus=[], argument_evaluation=[],
        risk_points=[], strategy_suggestions=[], evidence_suggestions=[],
    )
    assert resp.dispute_focus == []


# ── Prompt constants ──


def test_trial_prompts_all_non_empty():
    from app.ai.prompts.trial_prompts import (
        TRIAL_INIT_SYSTEM_PROMPT,
        TRIAL_INIT_TEMPLATE,
        TRIAL_ATTACK_SYSTEM_PROMPT,
        TRIAL_ATTACK_TEMPLATE,
        TRIAL_EVALUATE_SYSTEM_PROMPT,
        TRIAL_EVALUATE_TEMPLATE,
        TRIAL_COUNTER_SYSTEM_PROMPT,
        TRIAL_COUNTER_TEMPLATE,
        TRIAL_REPORT_SYSTEM_PROMPT,
        TRIAL_REPORT_TEMPLATE,
    )
    prompts = [
        TRIAL_INIT_SYSTEM_PROMPT, TRIAL_INIT_TEMPLATE,
        TRIAL_ATTACK_SYSTEM_PROMPT, TRIAL_ATTACK_TEMPLATE,
        TRIAL_EVALUATE_SYSTEM_PROMPT, TRIAL_EVALUATE_TEMPLATE,
        TRIAL_COUNTER_SYSTEM_PROMPT, TRIAL_COUNTER_TEMPLATE,
        TRIAL_REPORT_SYSTEM_PROMPT, TRIAL_REPORT_TEMPLATE,
    ]
    for p in prompts:
        assert isinstance(p, str)
        assert len(p) > 0


def test_trial_init_template_has_placeholders():
    from app.ai.prompts.trial_prompts import TRIAL_INIT_TEMPLATE
    assert "{title}" in TRIAL_INIT_TEMPLATE
    assert "{case_type}" in TRIAL_INIT_TEMPLATE
    assert "{plaintiff}" in TRIAL_INIT_TEMPLATE
    assert "{dispute_focus}" in TRIAL_INIT_TEMPLATE


# ── Graph functions exist ──


def test_trial_graph_functions_callable():
    from app.ai.graphs.trial_graph import (
        init_simulation,
        ai_attack,
        evaluate_argument,
        ai_counter,
        generate_strategy_report,
    )
    for fn in [init_simulation, ai_attack, evaluate_argument, ai_counter, generate_strategy_report]:
        assert callable(fn)


def test_trial_state_is_typed_dict():
    from app.ai.graphs.trial_graph import TrialState
    annotations = TrialState.__annotations__
    assert "case_data" in annotations
    assert "mode" in annotations
    assert "dispute_focus" in annotations
    assert "strategy_report" in annotations
    assert "error" in annotations


# ── Service functions exist ──


def test_trial_service_functions_callable():
    from app.services.trial_service import (
        create_simulation,
        get_simulation,
        list_simulations,
        add_round,
        get_rounds,
        update_simulation,
    )
    for fn in [create_simulation, get_simulation, list_simulations, add_round, get_rounds, update_simulation]:
        assert callable(fn)


# ── get_opponent_role logic ──


def test_get_opponent_role_defense_mode():
    from app.ai.graphs.trial_graph import _get_opponent_role
    assert _get_opponent_role("defense", "plaintiff") == "原告代理律师"
    assert _get_opponent_role("defense", "defendant") == "被告代理律师"


def test_get_opponent_role_judgment_mode():
    from app.ai.graphs.trial_graph import _get_opponent_role
    assert _get_opponent_role("judgment", "plaintiff") == "对方律师"
    assert _get_opponent_role("judgment", "defendant") == "对方律师"


def test_get_opponent_role_unknown_mode():
    from app.ai.graphs.trial_graph import _get_opponent_role
    assert _get_opponent_role("unknown", "plaintiff") == "对方律师"


# ── Trial graph: ai_counter with mock ──


@pytest.mark.asyncio
@patch("app.ai.graphs.trial_graph.get_openai_client")
async def test_ai_counter(MockGetClient):
    from app.ai.graphs.trial_graph import ai_counter
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = "继续追问：你方如何解释考勤记录的缺失？"
    MockGetClient.return_value.chat.completions.create = AsyncMock(return_value=mock_resp)
    state = await ai_counter({
        "mode": "arbitration", "user_role": "plaintiff",
        "current_round": 2, "ai_message": "质疑内容",
        "user_message": "回应", "dispute_focus": ["加班费"],
        "evaluation": {"strength": "medium", "score": 55},
        "error": "",
    })
    assert "追问" in state["ai_message"]
    assert state["error"] == ""
