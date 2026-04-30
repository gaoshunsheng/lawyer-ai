"""
用户模型
"""
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, SmallInteger, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class Tenant(Base):
    """租户模型（律所）"""
    __tablename__ = "tenants"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="律所名称")
    code = Column(String(50), nullable=False, unique=True, comment="律所编码")
    contact_person = Column(String(50), comment="联系人")
    contact_phone = Column(String(20), comment="联系电话")
    address = Column(String(200), comment="地址")
    status = Column(Integer, default=1, comment="状态：0-禁用，1-启用")
    expire_time = Column(DateTime, comment="到期时间")
    max_users = Column(Integer, default=10, comment="最大用户数")
    current_user_count = Column(Integer, default=0, comment="当前用户数")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(BigInteger)
    updated_by = Column(BigInteger)
    is_deleted = Column(SmallInteger, default=0)

    # 关系
    users = relationship("User", back_populates="tenant")


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True, comment="用户名")
    password = Column(String(100), nullable=False, comment="密码")
    real_name = Column(String(50), comment="真实姓名")
    phone = Column(String(20), comment="手机号")
    email = Column(String(100), comment="邮箱")
    role = Column(String(20), nullable=False, comment="角色")
    tenant_id = Column(BigInteger, ForeignKey("tenants.id"), comment="租户ID")
    avatar = Column(String(200), comment="头像URL")
    status = Column(Integer, default=1, comment="状态：0-禁用，1-启用")
    last_login_time = Column(DateTime, comment="最后登录时间")
    last_login_ip = Column(String(50), comment="最后登录IP")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(BigInteger)
    updated_by = Column(BigInteger)
    is_deleted = Column(SmallInteger, default=0)

    # 关系
    tenant = relationship("Tenant", back_populates="users")


class ChatSession(Base):
    """聊天会话模型"""
    __tablename__ = "chat_sessions"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, comment="用户ID")
    title = Column(String(200), comment="会话标题")
    case_id = Column(BigInteger, comment="关联案件ID")
    tenant_id = Column(BigInteger, nullable=False, comment="租户ID")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(SmallInteger, default=0)

    # 关系
    messages = relationship("ChatMessage", back_populates="session")


class ChatMessage(Base):
    """聊天消息模型"""
    __tablename__ = "chat_messages"

    id = Column(BigInteger, primary_key=True, index=True)
    session_id = Column(BigInteger, ForeignKey("chat_sessions.id"), nullable=False, comment="会话ID")
    role = Column(String(20), nullable=False, comment="角色：user/assistant")
    content = Column(Text, nullable=False, comment="消息内容")
    tokens = Column(Integer, comment="Token数")
    metadata = Column(Text, comment="元数据JSON")
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    session = relationship("ChatSession", back_populates="messages")
