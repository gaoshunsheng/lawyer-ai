"""
聊天服务 - 增强版，支持RAG
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import ChatSession, ChatMessage
from app.schemas.common import ChatRequest as ChatRequestSchema
from app.schemas.chat import (
    ChatResponse as ChatResponseSchema,
    SessionInfo, MessageInfo, LegalBasis, CaseReference
)
from app.services.rag_service import RAGService
from app.core.config import settings

import logging

logger = logging.getLogger(__name__)


class ChatService:
    """聊天服务类"""

    def __init__(self):
        self.rag_service = RAGService()

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

    async def process_message(
            self,
            db: AsyncSession,
            user_id: int,
            tenant_id: Optional[int],
            request: ChatRequestSchema
    ) -> ChatResponseSchema:
        """
        处理聊天消息

        Args:
            db: 数据库会话
            user_id: 用户ID
            tenant_id: 租户ID
            request: 聊天请求

        Returns:
            聊天响应
        """
        # 获取或创建会话
        session = None
        if request.session_id:
            session = await self.get_session(db, request.session_id, user_id)
            if not session:
                session = await self.create_session(
                    db, user_id, tenant_id, request.case_id
                )
        else:
            session = await self.create_session(
                db, user_id, tenant_id, request.case_id
            )

        # 保存用户消息
        await self.add_message(
            db=db,
            session_id=session.id,
            role="user",
            content=request.content
        )

        # 使用RAG服务生成响应
        try:
            rag_result = await self.rag_service.chat_with_rag(
                query=request.content,
                history=[],
                stream=False
            )

            assistant_content = rag_result.get("content", "")
            search_results = rag_result.get("search_results", [])
            tokens_used = rag_result.get("tokens_used", 0)

        except Exception as e:
            logger.error(f"RAG服务调用失败: {e}")
            # 降级到模拟响应
            assistant_content = await self._generate_fallback_response(request.content)
            tokens_used = len(assistant_content) // 2
            search_results = []

        # 保存助手响应
        ai_message = await self.add_message(
            db=db,
            session_id=session.id,
            role="assistant",
            content=assistant_content,
            tokens=tokens_used
        )

        # 更新会话标题（如果是新会话）
        if session.title == "新会话":
            # 使用用户消息的前20个字符作为标题
            new_title = request.content[:20] + "..." if len(request.content) > 20 else request.content
            await self.update_session_title(db, session.id, new_title)

        # 构建法律依据
        legal_basis = []
        for result in search_results[:3]:  # 最多显示3条
            if result.source_type == "law":
                legal_basis.append(LegalBasis(
                    law_name=result.source_name,
                    article_number=result.metadata.get("article_number", ""),
                    content=result.content[:200] + "..." if len(result.content) > 200 else result.content,
                    url=f"/api/v1/knowledge/{result.id}"
                ))

        # 构建案例引用
        cases_referenced = []
        for result in search_results[:3]:
            if result.source_type == "case":
                cases_referenced.append(CaseReference(
                    case_number=result.metadata.get("case_number", ""),
                    court=result.metadata.get("court", ""),
                    date=result.metadata.get("date", ""),
                    summary=result.content[:150] + "..." if len(result.content) > 150 else result.content,
                    result=result.metadata.get("result", ""),
                    similarity=result.score
                ))

        # 返回响应
        return ChatResponseSchema(
            message_id=str(ai_message.id),
            session_id=session.id,
            role="assistant",
            content=assistant_content,
            content_type="text",
            legal_basis=legal_basis if legal_basis else None,
            cases_referenced=cases_referenced if cases_referenced else None,
            tokens_used=tokens_used,
            created_at=ai_message.created_at
        )

    async def _generate_fallback_response(self, user_message: str) -> str:
        """生成降级响应"""
        if "违法解除" in user_message or "解除劳动合同" in user_message:
            return """根据您咨询的问题，分析如下：

【法律依据】
• 《劳动合同法》第39条：劳动者严重违纪，用人单位可单方解除
• 《劳动合同法》第48条：违法解除的救济途径
• 《劳动合同法》第87条：违法解除双倍赔偿

【建议】
1. 收集公司规章制度公示证据
2. 保存考勤记录、工作记录等证据
3. 如有录音、聊天记录等，妥善保存

如需详细分析，请提供更多案件细节。"""

        elif "加班" in user_message:
            return """关于加班费问题：

【计算标准】
• 工作日加班：小时工资 × 150%
• 休息日加班：小时工资 × 200%
• 法定节假日加班：小时工资 × 300%

小时工资 = 月工资 ÷ 21.75 ÷ 8

【建议】
收集考勤记录、加班审批记录、工作记录等证据。"""

        else:
            return f"""您好，我是您的法律助手。

您的问题是：{user_message}

我可以为您提供劳动法相关的法律咨询服务，包括：
- 劳动合同纠纷
- 工资报酬争议
- 工伤赔偿
- 违法解除赔偿计算

请问您具体想咨询什么问题？"""
