"""
聊天路由 - 增强版
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.common import ResponseModel
from app.schemas.chat import (
    ChatRequest as ChatRequestSchema,
    ChatResponse as ChatResponseSchema,
    SessionInfo, MessageInfo, LegalBasis, CaseReference,
    CreateSessionRequest
)
from app.services.chat_service_enhanced import ChatService
from datetime import datetime
import uuid

router = APIRouter()

# 全局聊天服务实例
_chat_service = None


def get_chat_service() -> ChatService:
    """获取聊天服务实例"""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service


def get_user_id(x_user_id: Optional[str] = Header(None)) -> int:
    """从请求头获取用户ID"""
    if x_user_id:
        return int(x_user_id)
    return 1  # 默认用户ID，实际应该从JWT令牌解析


def get_tenant_id(x_tenant_id: Optional[str] = Header(None)) -> Optional[int]:
    """从请求头获取租户ID"""
    if x_tenant_id:
        return int(x_tenant_id)
    return None


@router.post("/sessions", response_model=ResponseModel)
async def create_session(
        request: CreateSessionRequest = None,
        db: AsyncSession = Depends(get_session),
        user_id: int = Depends(get_user_id),
        tenant_id: Optional[int] = Depends(get_tenant_id)
):
    """创建聊天会话"""
    chat_service = get_chat_service()

    if request is None:
        request = CreateSessionRequest()

    session = await chat_service.create_session(
        db=db,
        user_id=user_id,
        tenant_id=tenant_id,
        case_id=request.case_id,
        title=request.title
    )

    return ResponseModel(data=ChatService.session_to_info(session).model_dump())


@router.get("/sessions", response_model=ResponseModel)
async def list_sessions(
        page: int = 1,
        size: int = 20,
        db: AsyncSession = Depends(get_session),
        user_id: int = Depends(get_user_id)
):
    """获取用户的会话列表"""
    chat_service = get_chat_service()
    sessions = await chat_service.get_user_sessions(db, user_id, page, size)
    session_list = [ChatService.session_to_info(s).model_dump() for s in sessions]

    return ResponseModel(data={
        "list": session_list,
        "pagination": {
            "page": page,
            "page_size": size,
            "total": len(session_list)
        }
    })


@router.post("/message", response_model=ResponseModel)
async def send_message(
        request: ChatRequestSchema,
        db: AsyncSession = Depends(get_session),
        user_id: int = Depends(get_user_id),
        tenant_id: Optional[int] = Depends(get_tenant_id)
):
    """发送聊天消息"""
    chat_service = get_chat_service()

    response = await chat_service.process_message(
        db=db,
        user_id=user_id,
        tenant_id=tenant_id,
        request=request
    )

    return ResponseModel(data=response.model_dump())


@router.post("/sessions/{session_id}/messages", response_model=ResponseModel)
async def send_session_message(
        session_id: int,
        request: ChatRequestSchema,
        db: AsyncSession = Depends(get_session),
        user_id: int = Depends(get_user_id),
        tenant_id: Optional[int] = Depends(get_tenant_id)
):
    """发送消息到指定会话"""
    request.session_id = session_id
    return await send_message(request, db, user_id, tenant_id)


@router.get("/sessions/{session_id}/messages", response_model=ResponseModel)
async def get_messages(
        session_id: int,
        page: int = 1,
        size: int = 20,
        db: AsyncSession = Depends(get_session),
        user_id: int = Depends(get_user_id)
):
    """获取会话的消息历史"""
    chat_service = get_chat_service()

    # 验证会话归属
    session = await chat_service.get_session(db, session_id, user_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )

    messages = await chat_service.get_session_messages(db, session_id, page, size)
    message_list = [ChatService.message_to_info(m).model_dump() for m in messages]

    return ResponseModel(data={
        "list": message_list,
        "pagination": {
            "page": page,
            "page_size": size,
            "total": len(message_list)
        }
    })


@router.delete("/sessions/{session_id}", response_model=ResponseModel)
async def delete_session(
        session_id: int,
        db: AsyncSession = Depends(get_session),
        user_id: int = Depends(get_user_id)
):
    """删除会话"""
    chat_service = get_chat_service()
    success = await chat_service.delete_session(db, session_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    return ResponseModel(message="会话已删除")
