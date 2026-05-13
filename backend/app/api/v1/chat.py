import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.graphs.consult_graph import run_consultation, run_consultation_stream
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.chat import (
    ChatMessageResponse,
    ChatMessageSend,
    ChatSessionCreate,
    ChatSessionResponse,
)
from app.services.chat_service import (
    create_session,
    get_session_messages,
    get_user_sessions,
    save_message,
)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/sessions", response_model=ChatSessionResponse, status_code=201)
async def create_chat_session(
    req: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await create_session(db, current_user.id, current_user.tenant_id, req.title)
    return ChatSessionResponse.model_validate(session)


@router.get("/sessions", response_model=list[ChatSessionResponse])
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sessions = await get_user_sessions(db, current_user.id)
    return [ChatSessionResponse.model_validate(s) for s in sessions]


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageResponse])
async def get_messages(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    messages = await get_session_messages(db, session_id)
    return [ChatMessageResponse.model_validate(m) for m in messages]


@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: uuid.UUID,
    req: ChatMessageSend,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 获取历史消息
    history = await get_session_messages(db, session_id)
    messages = [{"role": m.role, "content": m.content} for m in history]

    # 保存用户消息
    await save_message(db, session_id, "user", req.content)

    # 流式生成回答
    async def stream_response():
        full_answer = ""
        async for chunk in run_consultation_stream(
            req.content,
            tenant_id=current_user.tenant_id,
            session_id=session_id,
            user_id=current_user.id,
            messages=messages,
        ):
            full_answer += chunk
            yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"

        # 保存AI回答
        await save_message(db, session_id, "assistant", full_answer)
        yield "data: [DONE]\n\n"

    return StreamingResponse(stream_response(), media_type="text/event-stream")
