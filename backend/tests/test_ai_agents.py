"""Tests for AI agent graphs — document, analysis, review, consult, and router."""

import json

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def _make_openai_mock(content, side_effect=None):
    """Helper: build an AsyncOpenAI mock that returns the given content."""
    mock_client = AsyncMock()
    if side_effect:
        mock_client.chat.completions.create.side_effect = side_effect
    else:
        mock_choice = MagicMock()
        mock_choice.message.content = content
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
    return mock_client


# ── Document Agent ──


@pytest.mark.asyncio
async def test_document_graph_structure():
    from app.ai.graphs.document_graph import build_document_graph

    graph = build_document_graph()
    assert graph is not None


@pytest.mark.asyncio
@patch("app.ai.graphs.document_graph.get_openai_client")
async def test_document_generate_node_success(MockGetClient):
    from app.ai.graphs.document_graph import generate_document_node

    MockGetClient.return_value = _make_openai_mock("生成的文书内容")

    state = {
        "template_name": "劳动争议仲裁申请书",
        "doc_type": "arbitration_application",
        "template_content": "模板 {{变量}}",
        "variables": {"变量": "测试值"},
        "instructions": "",
        "case_info": "",
        "generated_content": "",
        "error": "",
    }
    result = await generate_document_node(state)
    assert result["generated_content"] == "生成的文书内容"
    assert result["error"] == ""


@pytest.mark.asyncio
@patch("app.ai.graphs.document_graph.get_openai_client")
async def test_document_generate_node_api_error(MockGetClient):
    from app.ai.graphs.document_graph import generate_document_node

    MockGetClient.side_effect = Exception("API error")

    state = {
        "template_name": "test",
        "doc_type": "test",
        "template_content": "",
        "variables": {},
        "instructions": "",
        "case_info": "",
        "generated_content": "",
        "error": "",
    }
    result = await generate_document_node(state)
    assert result["generated_content"] == ""
    assert "API error" in result["error"]


@pytest.mark.asyncio
@patch("app.ai.graphs.document_graph.get_openai_client")
async def test_document_generate_node_empty_response(MockGetClient):
    from app.ai.graphs.document_graph import generate_document_node

    MockGetClient.return_value = _make_openai_mock(None)

    state = {
        "template_name": "test",
        "doc_type": "test",
        "template_content": "tpl",
        "variables": {},
        "instructions": "",
        "case_info": "",
        "generated_content": "",
        "error": "",
    }
    result = await generate_document_node(state)
    assert result["generated_content"] == ""
    assert result["error"] == ""


# ── Analysis Agent ──


@pytest.mark.asyncio
async def test_analysis_graph_structure():
    from app.ai.graphs.analysis_graph import build_analysis_graph

    graph = build_analysis_graph()
    assert graph is not None


@pytest.mark.asyncio
@patch("app.ai.graphs.analysis_graph.get_openai_client")
async def test_analysis_node_returns_json(MockGetClient):
    from app.ai.graphs.analysis_graph import analyze_node

    analysis_result = {
        "strengths": ["证据充分"],
        "weaknesses": ["时效风险"],
        "risks": [{"level": "medium", "description": "证据可能过期"}],
        "strategy": ["尽快提交"],
        "win_prediction": {"probability": 70, "reasoning": "证据充分"},
    }
    MockGetClient.return_value = _make_openai_mock(json.dumps(analysis_result))

    state = {
        "case_data": {"title": "测试案件", "case_type": "labor_contract"},
        "result": {},
        "error": "",
    }
    result = await analyze_node(state)
    assert "strengths" in result["result"]
    assert result["error"] == ""


@pytest.mark.asyncio
@patch("app.ai.graphs.analysis_graph.get_openai_client")
async def test_analysis_node_api_error(MockGetClient):
    from app.ai.graphs.analysis_graph import analyze_node

    MockGetClient.side_effect = Exception("Network timeout")

    state = {
        "case_data": {"title": "测试案件"},
        "result": {},
        "error": "",
    }
    result = await analyze_node(state)
    assert result["result"] == {}
    assert "Network timeout" in result["error"]


@pytest.mark.asyncio
@patch("app.ai.graphs.analysis_graph.get_openai_client")
async def test_analysis_node_with_full_case_data(MockGetClient):
    from app.ai.graphs.analysis_graph import analyze_node

    MockGetClient.return_value = _make_openai_mock(
        json.dumps({"strengths": [], "win_prediction": {}})
    )

    state = {
        "case_data": {
            "title": "劳动合同纠纷",
            "case_type": "labor_contract",
            "plaintiff": {"name": "张三"},
            "defendant": {"name": "某公司"},
            "claim_amount": "50000",
            "dispute_focus": ["加班费", "经济补偿金"],
            "evidences": [{"name": "工资条"}],
            "timeline": [{"date": "2024-01-01", "event": "入职"}],
        },
        "result": {},
        "error": "",
    }
    result = await analyze_node(state)
    assert result["result"] == {"strengths": [], "win_prediction": {}}
    assert result["error"] == ""

    # Verify prompt was built with all fields
    call_args = MockGetClient.return_value.chat.completions.create.call_args
    user_message = call_args.kwargs["messages"][1]["content"]
    assert "劳动合同纠纷" in user_message
    assert "加班费" in user_message


# ── Review Agent ──


@pytest.mark.asyncio
async def test_review_graph_structure():
    from app.ai.graphs.review_graph import build_review_graph

    graph = build_review_graph()
    assert graph is not None


@pytest.mark.asyncio
@patch("app.ai.graphs.review_graph.get_openai_client")
async def test_review_node_returns_structured_report(MockGetClient):
    from app.ai.graphs.review_graph import review_node

    review_result = {
        "overall_score": 75,
        "compliance": {"passed": ["合同期限"], "missing": ["工作地点"]},
        "risks": [{"level": "high", "description": "试用期过长"}],
        "suggestions": ["补充工作地点条款"],
    }
    MockGetClient.return_value = _make_openai_mock(json.dumps(review_result))

    state = {
        "contract_text": "劳动合同...",
        "user_concerns": "",
        "result": {},
        "error": "",
    }
    result = await review_node(state)
    assert "overall_score" in result["result"]
    assert result["error"] == ""


@pytest.mark.asyncio
@patch("app.ai.graphs.review_graph.get_openai_client")
async def test_review_node_api_error(MockGetClient):
    from app.ai.graphs.review_graph import review_node

    MockGetClient.side_effect = Exception("Rate limit exceeded")

    state = {
        "contract_text": "合同内容",
        "user_concerns": "",
        "result": {},
        "error": "",
    }
    result = await review_node(state)
    assert result["result"] == {}
    assert "Rate limit exceeded" in result["error"]


@pytest.mark.asyncio
@patch("app.ai.graphs.review_graph.get_openai_client")
async def test_review_node_with_user_concerns(MockGetClient):
    from app.ai.graphs.review_graph import review_node

    MockGetClient.return_value = _make_openai_mock(
        json.dumps({"overall_score": 80})
    )

    state = {
        "contract_text": "劳动合同",
        "user_concerns": "加班费和年假",
        "result": {},
        "error": "",
    }
    result = await review_node(state)
    assert result["result"]["overall_score"] == 80

    # Verify user concerns passed into prompt
    call_args = MockGetClient.return_value.chat.completions.create.call_args
    user_message = call_args.kwargs["messages"][1]["content"]
    assert "加班费和年假" in user_message


# ── Consult Agent ──


@pytest.mark.asyncio
async def test_consult_graph_structure():
    from app.ai.graphs.consult_graph import build_consult_graph

    graph = build_consult_graph()
    assert graph is not None


@pytest.mark.asyncio
@patch("app.ai.graphs.consult_graph.httpx.AsyncClient")
async def test_consult_classify_intent_returns_valid(MockClient):
    from app.ai.graphs.consult_graph import classify_intent, AgentState

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "law"}}]
    }
    mock_response.raise_for_status = MagicMock()

    mock_client_instance = AsyncMock()
    mock_client_instance.post.return_value = mock_response
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=False)
    MockClient.return_value = mock_client_instance

    state = AgentState(question="劳动法规定的加班费怎么算？")
    result = await classify_intent(state)
    assert result["intent"] == "law"


@pytest.mark.asyncio
@patch("app.ai.graphs.consult_graph.httpx.AsyncClient")
async def test_consult_classify_intent_fallback_on_error(MockClient):
    from app.ai.graphs.consult_graph import classify_intent, AgentState

    mock_client_instance = AsyncMock()
    mock_client_instance.post.side_effect = Exception("Connection refused")
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=False)
    MockClient.return_value = mock_client_instance

    state = AgentState(question="测试问题")
    result = await classify_intent(state)
    assert result["intent"] == "both"


@pytest.mark.asyncio
@patch("app.ai.graphs.consult_graph.httpx.AsyncClient")
async def test_consult_generate_answer(MockClient):
    from app.ai.graphs.consult_graph import generate_answer, AgentState

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "根据劳动法规定..."}}]
    }
    mock_response.raise_for_status = MagicMock()

    mock_client_instance = AsyncMock()
    mock_client_instance.post.return_value = mock_response
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=False)
    MockClient.return_value = mock_client_instance

    state = AgentState(question="加班费怎么算？", context="相关法条内容")
    result = await generate_answer(state)
    assert result["answer"] == "根据劳动法规定..."


# ── Router ──


def test_router_routes():
    from app.ai.graphs.router_graph import ROUTE_MAP, get_graph

    assert "consult" in ROUTE_MAP
    assert "document" in ROUTE_MAP
    assert "analysis" in ROUTE_MAP
    assert "review" in ROUTE_MAP


def test_router_get_graph_returns_compiled():
    from app.ai.graphs.router_graph import get_graph

    graph = get_graph("analysis")
    assert graph is not None


def test_router_unknown_route():
    from app.ai.graphs.router_graph import get_graph

    with pytest.raises(ValueError, match="Unknown route|未知路由"):
        get_graph("unknown_route")
