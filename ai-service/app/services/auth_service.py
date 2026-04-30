"""
认证服务
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.models.user import User, Tenant
from app.schemas.common import TokenResponse, UserInfo
from app.core.config import settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """认证服务类"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """生成密码哈希"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(user_id: int, username: str, role: str, tenant_id: Optional[int] = None) -> str:
        """创建访问令牌"""
        # TODO: 实现JWT令牌生成
        # 这里简化处理，实际项目应使用PyJWT生成令牌
        import hashlib
        import time
        data = f"{user_id}:{username}:{role}:{tenant_id}:{time.time()}"
        return hashlib.sha256(data.encode()).hexdigest()

    @staticmethod
    def create_refresh_token(user_id: int, username: str) -> str:
        """创建刷新令牌"""
        import hashlib
        import time
        data = f"refresh:{user_id}:{username}:{time.time()}"
        return hashlib.sha256(data.encode()).hexdigest()

    @staticmethod
    async def authenticate_user(
            db: AsyncSession,
            username: str,
            password: str,
            client_ip: str = None
    ) -> Optional[dict]:
        """
        用户认证
        返回用户信息和令牌
        """
        # 查询用户
        result = await db.execute(
            select(User).where(User.username == username, User.is_deleted == 0)
        )
        user = result.scalar_one_or_none()

        if not user:
            return None

        # 验证密码
        if not AuthService.verify_password(password, user.password):
            return None

        # 检查用户状态
        if user.status != 1:
            return None

        # 检查租户状态
        if user.tenant_id:
            tenant_result = await db.execute(
                select(Tenant).where(Tenant.id == user.tenant_id)
            )
            tenant = tenant_result.scalar_one_or_none()
            if not tenant or tenant.status != 1:
                return None
            if tenant.expire_time and tenant.expire_time < datetime.utcnow():
                return None

        # 更新登录信息
        user.last_login_time = datetime.utcnow()
        user.last_login_ip = client_ip
        await db.commit()

        # 生成令牌
        access_token = AuthService.create_access_token(
            user.id, user.username, user.role, user.tenant_id
        )
        refresh_token = AuthService.create_refresh_token(user.id, user.username)

        # 获取租户名称
        tenant_name = None
        if user.tenant_id:
            tenant_result = await db.execute(
                select(Tenant).where(Tenant.id == user.tenant_id)
            )
            tenant = tenant_result.scalar_one_or_none()
            tenant_name = tenant.name if tenant else None

        # 构建用户信息
        user_info = UserInfo(
            id=user.id,
            username=user.username,
            real_name=user.real_name,
            phone=user.phone,
            email=user.email,
            role=user.role,
            role_name=AuthService.get_role_name(user.role),
            tenant_id=user.tenant_id,
            tenant_name=tenant_name,
            avatar=user.avatar,
            status=user.status
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": settings.JWT_EXPIRATION,
            "user_info": user_info
        }

    @staticmethod
    def get_role_name(role: str) -> str:
        """获取角色名称"""
        role_names = {
            "ADMIN": "系统管理员",
            "SENIOR_LAWYER": "主办律师",
            "JUNIOR_LAWYER": "辅助律师",
            "ASSISTANT": "律师助理",
            "ADMIN_STAFF": "行政人员"
        }
        return role_names.get(role, role)

    @staticmethod
    async def register_user(
            db: AsyncSession,
            username: str,
            password: str,
            real_name: str,
            phone: str = None,
            email: str = None,
            role: str = "ASSISTANT",
            tenant_id: int = None
    ) -> Optional[dict]:
        """
        用户注册
        """
        # 检查用户名是否存在
        result = await db.execute(
            select(User).where(User.username == username, User.is_deleted == 0)
        )
        if result.scalar_one_or_none():
            return None

        # 检查租户
        tenant = None
        if tenant_id:
            tenant_result = await db.execute(
                select(Tenant).where(Tenant.id == tenant_id)
            )
            tenant = tenant_result.scalar_one_or_none()
            if not tenant:
                return None
            if tenant.max_users and tenant.current_user_count >= tenant.max_users:
                return None

        # 创建用户
        hashed_password = AuthService.get_password_hash(password)
        user = User(
            username=username,
            password=hashed_password,
            real_name=real_name,
            phone=phone,
            email=email,
            role=role,
            tenant_id=tenant_id,
            status=1
        )
        db.add(user)

        # 更新租户用户数
        if tenant:
            tenant.current_user_count += 1

        await db.commit()
        await db.refresh(user)

        # 生成令牌
        access_token = AuthService.create_access_token(
            user.id, user.username, user.role, user.tenant_id
        )
        refresh_token = AuthService.create_refresh_token(user.id, user.username)

        # 构建用户信息
        user_info = UserInfo(
            id=user.id,
            username=user.username,
            real_name=user.real_name,
            phone=user.phone,
            email=user.email,
            role=user.role,
            role_name=AuthService.get_role_name(user.role),
            tenant_id=user.tenant_id,
            tenant_name=tenant.name if tenant else None,
            avatar=user.avatar,
            status=user.status
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": settings.JWT_EXPIRATION,
            "user_info": user_info
        }

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def change_password(
            db: AsyncSession,
            user_id: int,
            old_password: str,
            new_password: str
    ) -> bool:
        """修改密码"""
        user = await AuthService.get_user_by_id(db, user_id)
        if not user:
            return False

        # 验证原密码
        if not AuthService.verify_password(old_password, user.password):
            return False

        # 更新密码
        user.password = AuthService.get_password_hash(new_password)
        await db.commit()
        return True
