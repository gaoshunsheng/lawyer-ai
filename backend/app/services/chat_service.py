import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Case, ChatMessage, ChatSession


async def create_session(
    db: AsyncSession,
    user_id: uuid.UUID,
    tenant_id: uuid.UUID,
    title: str | None = None,
    case_id: uuid.UUID | None = None,
) -> ChatSession:
    session = ChatSession(
        tenant_id=tenant_id,
        user_id=user_id,
        title=title or "新对话",
        case_id=case_id,
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


async def get_session(db: AsyncSession, session_id: uuid.UUID) -> ChatSession | None:
    result = await db.execute(
        select(ChatSession).where(ChatSession.id == session_id)
    )
    return result.scalar_one_or_none()


async def get_session_messages(db: AsyncSession, session_id: uuid.UUID) -> list[ChatMessage]:
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
        .limit(200)
    )
    return list(result.scalars().all())


async def save_message(
    db: AsyncSession,
    session_id: uuid.UUID,
    role: str,
    content: str,
    tokens_used: int | None = None,
    is_follow_up: bool = False,
    attachments: dict | None = None,
) -> ChatMessage:
    message = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        tokens_used=tokens_used,
        is_follow_up=is_follow_up,
        attachments=attachments,
    )
    db.add(message)
    await db.flush()
    return message


async def link_case(db: AsyncSession, session_id: uuid.UUID, case_id: uuid.UUID) -> ChatSession | None:
    session = await get_session(db, session_id)
    if not session:
        return None
    session.case_id = case_id
    await db.flush()
    return session


async def unlink_case(db: AsyncSession, session_id: uuid.UUID) -> ChatSession | None:
    session = await get_session(db, session_id)
    if not session:
        return None
    session.case_id = None
    await db.flush()
    return session


async def get_linked_case(db: AsyncSession, session_id: uuid.UUID) -> Case | None:
    session = await get_session(db, session_id)
    if not session or not session.case_id:
        return None
    result = await db.execute(select(Case).where(Case.id == session.case_id))
    return result.scalar_one_or_none()


async def increment_follow_up_count(db: AsyncSession, session_id: uuid.UUID) -> None:
    await db.execute(
        update(ChatSession)
        .where(ChatSession.id == session_id)
        .values(follow_up_count=ChatSession.follow_up_count + 1)
    )
    await db.flush()
