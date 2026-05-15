"""Extra tests for consultation enhancement — schemas, file_parser, service, graph state."""

import uuid
import datetime
from unittest.mock import AsyncMock

import pytest

from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatMessageSend,
    ChatMessageResponse,
    LinkCaseRequest,
    FollowUpResult,
)


# ── ChatSessionCreate ──


def test_chat_session_create_with_case_id():
    case_id = uuid.uuid4()
    req = ChatSessionCreate(title="劳动纠纷咨询", case_id=case_id)
    assert req.case_id == case_id
    assert req.title == "劳动纠纷咨询"


def test_chat_session_create_without_case_id():
    req = ChatSessionCreate(title="普通咨询")
    assert req.case_id is None


def test_chat_session_create_defaults():
    req = ChatSessionCreate()
    assert req.title is None
    assert req.case_id is None


# ── ChatSessionResponse ──


def test_chat_session_response_with_follow_up_count():
    resp = ChatSessionResponse(
        id=uuid.uuid4(), title="咨询", status="active",
        case_id=None, follow_up_count=5, created_at=datetime.datetime.now(),
    )
    assert resp.follow_up_count == 5


def test_chat_session_response_with_case_id():
    case_id = uuid.uuid4()
    resp = ChatSessionResponse(
        id=uuid.uuid4(), title="案件咨询", status="active",
        case_id=case_id, follow_up_count=0, created_at=datetime.datetime.now(),
    )
    assert resp.case_id == case_id


def test_chat_session_response_default_follow_up():
    resp = ChatSessionResponse(
        id=uuid.uuid4(), title="测试", status="active",
        case_id=None, created_at=datetime.datetime.now(),
    )
    assert resp.follow_up_count == 0


# ── ChatMessageResponse ──


def test_chat_message_response_is_follow_up():
    resp = ChatMessageResponse(
        id=uuid.uuid4(), session_id=uuid.uuid4(), role="assistant",
        content="追问问题", tokens_used=30, is_follow_up=True,
        attachments=None, created_at=datetime.datetime.now(),
    )
    assert resp.is_follow_up is True


def test_chat_message_response_not_follow_up():
    resp = ChatMessageResponse(
        id=uuid.uuid4(), session_id=uuid.uuid4(), role="assistant",
        content="正常回复", tokens_used=50, is_follow_up=False,
        attachments=None, created_at=datetime.datetime.now(),
    )
    assert resp.is_follow_up is False


def test_chat_message_response_with_attachments():
    resp = ChatMessageResponse(
        id=uuid.uuid4(), session_id=uuid.uuid4(), role="system",
        content="文件上传", tokens_used=None, is_follow_up=False,
        attachments={"filename": "合同.pdf", "size": 2048, "pages": 3},
        created_at=datetime.datetime.now(),
    )
    assert resp.attachments["pages"] == 3
    assert resp.attachments["size"] == 2048


# ── LinkCaseRequest validation ──


def test_link_case_request_valid():
    case_id = uuid.uuid4()
    req = LinkCaseRequest(case_id=case_id)
    assert req.case_id == case_id


def test_link_case_request_missing_case_id():
    with pytest.raises(Exception):
        LinkCaseRequest()


# ── FollowUpResult combinations ──


def test_follow_up_result_with_missing_info():
    result = FollowUpResult(
        needs_follow_up=True,
        question="请问您的入职日期是？",
        missing_info=["入职日期", "工资标准", "合同期限"],
    )
    assert len(result.missing_info) == 3
    assert "入职日期" in result.missing_info


def test_follow_up_result_no_need_defaults():
    result = FollowUpResult(needs_follow_up=False)
    assert result.question is None
    assert result.missing_info == []


def test_follow_up_result_no_need_with_question():
    result = FollowUpResult(
        needs_follow_up=False,
        question=None,
        missing_info=[],
    )
    assert result.needs_follow_up is False


# ── file_parser tests ──


@pytest.mark.asyncio
async def test_parse_text_html_content_type():
    from app.services.file_parser import parse_file
    result = await parse_file("HTML内容".encode("utf-8"), "page.html", "text/html")
    assert "HTML" in result


@pytest.mark.asyncio
async def test_parse_text_plain_content_type():
    from app.services.file_parser import parse_file
    result = await parse_file(b"plain text content", "file.txt", "text/plain")
    assert "plain" in result


@pytest.mark.asyncio
async def test_parse_pdf_empty_content():
    from app.services.file_parser import parse_file
    result = await parse_file(b"", "test.pdf", "application/pdf")
    assert result == ""


@pytest.mark.asyncio
async def test_parse_docx_empty_content():
    from app.services.file_parser import parse_file
    result = await parse_file(b"", "test.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    assert result == ""


@pytest.mark.asyncio
async def test_parse_no_extension_returns_empty():
    from app.services.file_parser import parse_file
    result = await parse_file(b"some data", "noext", "application/octet-stream")
    assert result == ""


@pytest.mark.asyncio
async def test_parse_unknown_extension_returns_empty():
    from app.services.file_parser import parse_file
    result = await parse_file(b"data", "file.xyz", "application/octet-stream")
    assert result == ""


# ── Chat service functions exist ──


def test_chat_service_has_link_case():
    from app.services.chat_service import link_case
    assert callable(link_case)


def test_chat_service_has_unlink_case():
    from app.services.chat_service import unlink_case
    assert callable(unlink_case)


def test_chat_service_has_get_linked_case():
    from app.services.chat_service import get_linked_case
    assert callable(get_linked_case)


def test_chat_service_has_increment_follow_up_count():
    from app.services.chat_service import increment_follow_up_count
    assert callable(increment_follow_up_count)


# ── AgentState ──


def test_agent_state_has_case_context():
    from app.ai.graphs.consult_graph import AgentState
    state = AgentState(case_context="关联案件：劳动仲裁")
    assert state.case_context == "关联案件：劳动仲裁"


def test_agent_state_default_case_context():
    from app.ai.graphs.consult_graph import AgentState
    state = AgentState()
    assert state.case_context == ""


def test_agent_state_all_fields():
    from app.ai.graphs.consult_graph import AgentState
    state = AgentState(
        question="什么是加班费？",
        intent="law",
        context="劳动法相关条文",
        answer="根据劳动法...",
        tenant_id=uuid.uuid4(),
        session_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        messages=[],
        case_context="案件编号001",
    )
    assert state.question == "什么是加班费？"
    assert state.intent == "law"
    assert state.case_context == "案件编号001"


# ── Consult graph functions ──


def test_consult_graph_functions_callable():
    from app.ai.graphs.consult_graph import (
        classify_intent,
        rag_retrieve,
        generate_answer,
        check_follow_up,
        route_by_intent,
        build_consult_graph,
    )
    for fn in [classify_intent, rag_retrieve, generate_answer, check_follow_up, route_by_intent, build_consult_graph]:
        assert callable(fn)


def test_route_by_intent_general():
    from app.ai.graphs.consult_graph import route_by_intent, AgentState
    state = AgentState(intent="general")
    assert route_by_intent(state) == "generate"


def test_route_by_intent_law():
    from app.ai.graphs.consult_graph import route_by_intent, AgentState
    state = AgentState(intent="law")
    assert route_by_intent(state) == "retrieve"


def test_route_by_intent_case():
    from app.ai.graphs.consult_graph import route_by_intent, AgentState
    state = AgentState(intent="case")
    assert route_by_intent(state) == "retrieve"
