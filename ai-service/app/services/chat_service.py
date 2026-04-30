"""
聊天服务
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import ChatSession, ChatMessage
from app.schemas.common import ChatRequest, ChatResponse, SessionInfo, MessageInfo


class ChatService:
    """聊天服务类"""

    @staticmethod
    async def create_session(
            db: AsyncSession,
            user_id: int,
            tenant_id: Optional[int] = None,
            case_id: Optional[int] = None,
            title: Optional[str] = None
    ) -> ChatSession:
        """创建聊天会话"""
        session = ChatSession(
            user_id=user_id,
            tenant_id=tenant_id,
            case_id=case_id,
            title=title or "新会话"
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    @staticmethod
    async def get_session(db: AsyncSession, session_id: int, user_id: int) -> Optional[ChatSession]:
        """获取会话"""
        result = await db.execute(
            select(ChatSession).where(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id,
                ChatSession.is_deleted == 0
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_sessions(
            db: AsyncSession,
            user_id: int,
            page: int = 1,
            size: int = 20
    ) -> List[ChatSession]:
        """获取用户的会话列表"""
        offset = (page - 1) * size
        result = await db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id, ChatSession.is_deleted == 0)
            .order_by(ChatSession.updated_at.desc())
            .offset(offset)
            .limit(size)
        )
        return result.scalars().all()

    @staticmethod
    async def add_message(
            db: AsyncSession,
            session_id: int,
            role: str,
            content: str,
            tokens: Optional[int] = None,
            metadata: Optional[str] = None
    ) -> ChatMessage:
        """添加消息"""
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            tokens=tokens,
            metadata=metadata
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message

    @staticmethod
    async def get_session_messages(
            db: AsyncSession,
            session_id: int,
            page: int = 1,
            size: int = 20
    ) -> List[ChatMessage]:
        """获取会话的消息列表"""
        offset = (page - 1) * size
        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .offset(offset)
            .limit(size)
        )
        return result.scalars().all()

    @staticmethod
    async def delete_session(db: AsyncSession, session_id: int, user_id: int) -> bool:
        """删除会话"""
        session = await ChatService.get_session(db, session_id, user_id)
        if not session:
            return False
        session.is_deleted = 1
        await db.commit()
        return True

    @staticmethod
    async def update_session_title(db: AsyncSession, session_id: int, title: str) -> None:
        """更新会话标题"""
        result = await db.execute(
            select(ChatSession).where(ChatSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        if session:
            session.title = title
            await db.commit()

    @staticmethod
    def session_to_info(session: ChatSession) -> SessionInfo:
        """转换会话为SessionInfo"""
        return SessionInfo(
            id=session.id,
            user_id=session.user_id,
            title=session.title,
            case_id=session.case_id,
            tenant_id=session.tenant_id,
            created_at=session.created_at,
            updated_at=session.updated_at
        )

    @staticmethod
    def message_to_info(message: ChatMessage) -> MessageInfo:
        """转换消息为MessageInfo"""
        return MessageInfo(
            id=message.id,
            session_id=message.session_id,
            role=message.role,
            content=message.content,
            tokens=message.tokens,
            metadata=message.metadata,
            created_at=message.created_at
        )
