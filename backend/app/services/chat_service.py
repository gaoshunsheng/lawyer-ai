import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ChatMessage, ChatSession


async def create_session(db: AsyncSession, user_id: uuid.UUID, tenant_id: uuid.UUID, title: str | None = None) -> ChatSession:
    session = ChatSession(
        tenant_id=tenant_id,
        user_id=user_id,
        title=title or "新对话",
    )
    db.add(session)
    await db.flush()
    return session


async def get_user_sessions(db: AsyncSession, user_id: uuid.UUID) -> list[ChatSession]:
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == user_id, ChatSession.status == "active")
        .order_by(ChatSession.updated_at.desc())
    )
    return list(result.scalars().all())


async def get_session_messages(db: AsyncSession, session_id: uuid.UUID) -> list[ChatMessage]:
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    return list(result.scalars().all())


async def save_message(db: AsyncSession, session_id: uuid.UUID, role: str, content: str, tokens_used: int | None = None) -> ChatMessage:
    message = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        tokens_used=tokens_used,
    )
    db.add(message)
    await db.flush()
    return message
