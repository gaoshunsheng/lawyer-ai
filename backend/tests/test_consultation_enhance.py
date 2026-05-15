import pytest
from io import BytesIO

from app.schemas.chat import (
    ChatMessageSend,
    ChatSessionCreate,
    ChatSessionResponse,
    ChatMessageResponse,
    LinkCaseRequest,
    FollowUpResult,
)
from app.services.file_parser import parse_file


# --- file_parser tests ---

@pytest.mark.asyncio
async def test_parse_text_file():
    result = await parse_file(b"hello world", "test.txt", "text/plain")
    assert "hello" in result


@pytest.mark.asyncio
async def test_parse_text_utf8():
    result = await parse_file("中文内容".encode("utf-8"), "test.txt", "text/plain")
    assert "中文" in result


@pytest.mark.asyncio
async def test_parse_text_with_charset():
    result = await parse_file(b"hello", "test.txt", "text/html; charset=utf-8")
    assert "hello" in result


@pytest.mark.asyncio
async def test_parse_empty_pdf():
    result = await parse_file(b"", "test.pdf", "application/pdf")
    assert result == ""


@pytest.mark.asyncio
async def test_parse_unsupported_format():
    result = await parse_file(b"\x00\x01", "test.xyz", "application/octet-stream")
    assert result == ""


@pytest.mark.asyncio
async def test_parse_no_extension():
    result = await parse_file(b"data", "README", "application/octet-stream")
    assert result == ""


# --- schema tests ---

def test_chat_session_create_with_case_id():
    import uuid
    case_id = uuid.uuid4()
    req = ChatSessionCreate(title="劳动纠纷咨询", case_id=case_id)
    assert req.case_id == case_id
    assert req.title == "劳动纠纷咨询"


def test_chat_session_create_default():
    req = ChatSessionCreate()
    assert req.title is None
    assert req.case_id is None


def test_chat_message_send_with_attachment():
    req = ChatMessageSend(content="请帮我看看", attachment_text="合同内容...")
    assert req.attachment_text == "合同内容..."


def test_chat_message_send_no_attachment():
    req = ChatMessageSend(content="你好")
    assert req.attachment_text is None


def test_link_case_request():
    import uuid
    case_id = uuid.uuid4()
    req = LinkCaseRequest(case_id=case_id)
    assert req.case_id == case_id


def test_follow_up_result_needs():
    result = FollowUpResult(
        needs_follow_up=True,
        question="请问您的工资标准是多少？",
        missing_info=["工资标准"],
    )
    assert result.needs_follow_up is True
    assert "工资标准" in result.missing_info


def test_follow_up_result_no_need():
    result = FollowUpResult(needs_follow_up=False)
    assert result.question is None
    assert result.missing_info == []


def test_chat_session_response_schema():
    import uuid
    import datetime
    resp = ChatSessionResponse(
        id=uuid.uuid4(),
        title="测试会话",
        status="active",
        case_id=None,
        follow_up_count=2,
        created_at=datetime.datetime.now(),
    )
    assert resp.follow_up_count == 2
    assert resp.case_id is None


def test_chat_message_response_with_follow_up():
    import uuid
    import datetime
    resp = ChatMessageResponse(
        id=uuid.uuid4(),
        session_id=uuid.uuid4(),
        role="assistant",
        content="请问您的工作时间是怎样的？",
        tokens_used=50,
        is_follow_up=True,
        attachments=None,
        created_at=datetime.datetime.now(),
    )
    assert resp.is_follow_up is True


def test_chat_message_response_with_attachments():
    import uuid
    import datetime
    resp = ChatMessageResponse(
        id=uuid.uuid4(),
        session_id=uuid.uuid4(),
        role="system",
        content="用户上传了文件",
        tokens_used=None,
        is_follow_up=False,
        attachments={"filename": "contract.pdf", "size": 1024},
        created_at=datetime.datetime.now(),
    )
    assert resp.attachments["filename"] == "contract.pdf"


# --- consult_graph check_follow_up test ---

def test_check_follow_up_import():
    from app.ai.graphs.consult_graph import check_follow_up
    assert callable(check_follow_up)


def test_consult_graph_has_case_context():
    from app.ai.graphs.consult_graph import AgentState
    state = AgentState(case_context="关联案件：劳动仲裁")
    assert state.case_context == "关联案件：劳动仲裁"
