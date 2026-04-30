"""
认证路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.common import (
    ResponseModel, LoginRequest, RegisterRequest,
    RefreshTokenRequest, ChangePasswordRequest,
    LoginResponse, UserInfo
)
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["认证管理"])
security = HTTPBearer()


@router.post("/login", response_model=ResponseModel[LoginResponse], summary="用户登录")
async def login(
        request: Request,
        data: LoginRequest,
        db: AsyncSession = Depends(get_session)
):
    """
    用户登录接口
    - **username**: 用户名
    - **password**: 密码
    """
    # 获取客户端IP
    client_ip = request.client.host
    if "x-forwarded-for" in request.headers:
        client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()

    result = await AuthService.authenticate_user(
        db, data.username, data.password, client_ip
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    return ResponseModel(data=LoginResponse(**result))


@router.post("/register", response_model=ResponseModel[LoginResponse], summary="用户注册")
async def register(
        data: RegisterRequest,
        db: AsyncSession = Depends(get_session)
):
    """
    用户注册接口
    - **username**: 用户名（3-50字符）
    - **password**: 密码（6-100字符）
    - **real_name**: 真实姓名
    - **phone**: 手机号（可选）
    - **email**: 邮箱（可选）
    - **role**: 角色（可选，默认ASSISTANT）
    - **tenant_id**: 租户ID（可选）
    """
    result = await AuthService.register_user(
        db=db,
        username=data.username,
        password=data.password,
        real_name=data.real_name,
        phone=getattr(data, 'phone', None),
        email=getattr(data, 'email', None),
        role=getattr(data, 'role', 'ASSISTANT'),
        tenant_id=getattr(data, 'tenant_id', None)
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="注册失败，用户名可能已存在或租户限制"
        )

    return ResponseModel(data=LoginResponse(**result))


@router.post("/refresh", response_model=ResponseModel[LoginResponse], summary="刷新令牌")
async def refresh_token(
        data: RefreshTokenRequest,
        db: AsyncSession = Depends(get_session)
):
    """
    刷新令牌接口
    - **refresh_token**: 刷新令牌
    """
    # TODO: 实现令牌刷新逻辑
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="功能开发中"
    )


@router.get("/me", response_model=ResponseModel[UserInfo], summary="获取当前用户信息")
async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_session)
):
    """
    获取当前登录用户信息
    """
    # TODO: 从JWT令牌解析用户ID
    # 目前返回示例数据
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="功能开发中"
    )


@router.put("/password", response_model=ResponseModel, summary="修改密码")
async def change_password(
        data: ChangePasswordRequest,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_session)
):
    """
    修改密码接口
    - **old_password**: 原密码
    - **new_password**: 新密码
    """
    # TODO: 从JWT令牌解析用户ID并验证
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="功能开发中"
    )


@router.post("/logout", response_model=ResponseModel, summary="登出")
async def logout(
        credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    登出接口（客户端清除令牌即可）
    """
    return ResponseModel(message="登出成功")