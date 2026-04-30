"""
聊天相关Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class ChatMessageBase(BaseModel):
    """聊天消息基础模型"""
    role: str = Field(description="角色: user/assistant/system")
    content: str = Field(description="消息内容")


class ChatRequest(BaseModel):
    """聊天请求"""
    content: str = Field(..., description="消息内容", min_length=1, max_length=10000)
    session_id: Optional[int] = Field(default=None, description="会话ID")
    case_id: Optional[int] = Field(default=None, description="关联案件ID")
    attachments: Optional[List[dict]] = Field(default=None, description="附件")
    stream: bool = Field(default=False, description="是否流式输出")


class LegalBasis(BaseModel):
    """法律依据"""
    law_name: str = Field(description="法律名称")
    article_number: str = Field(description="条款号")
    content: str = Field(description="条款内容")
    url: Optional[str] = Field(default=None, description="链接")


class CaseReference(BaseModel):
    """案例引用"""
    case_number: str = Field(description="案号")
    court: str = Field(description="法院")
    date: str = Field(description="日期")
    summary: str = Field(description="摘要")
    result: str = Field(description="判决结果")
    similarity: float = Field(description="相似度")


class ChatResponse(BaseModel):
    """聊天响应"""
    message_id: str = Field(description="消息ID")
    session_id: Optional[int] = Field(default=None, description="会话ID")
    role: str = Field(description="角色")
    content: str = Field(description="消息内容")
    content_type: str = Field(default="text", description="内容类型")
    legal_basis: Optional[List[LegalBasis]] = Field(default=None, description="法律依据")
    cases_referenced: Optional[List[CaseReference]] = Field(default=None, description="引用案例")
    tokens_used: Optional[int] = Field(default=None, description="消耗Token数")
    created_at: datetime = Field(description="创建时间")


class SessionInfo(BaseModel):
    """会话信息"""
    id: int = Field(description="会话ID")
    user_id: int = Field(description="用户ID")
    title: str = Field(description="会话标题")
    case_id: Optional[int] = Field(default=None, description="关联案件ID")
    tenant_id: Optional[int] = Field(default=None, description="租户ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class MessageInfo(BaseModel):
    """消息信息"""
    id: int = Field(description="消息ID")
    session_id: int = Field(description="会话ID")
    role: str = Field(description="角色: user/assistant")
    content: str = Field(description="消息内容")
    tokens: Optional[int] = Field(default=None, description="Token数")
    metadata: Optional[str] = Field(default=None, description="元数据")
    created_at: datetime = Field(description="创建时间")


class CreateSessionRequest(BaseModel):
    """创建会话请求"""
    case_id: Optional[int] = Field(default=None, description="关联案件ID")
    title: Optional[str] = Field(default=None, description="会话标题")
