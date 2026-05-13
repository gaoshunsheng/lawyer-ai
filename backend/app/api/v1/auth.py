from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserBrief
from app.services.user_service import authenticate_user, create_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await create_user(db, req.username, req.email, req.password, req.real_name)
    access = create_access_token(str(user.id), {"tenant_id": str(user.tenant_id), "role": user.role})
    refresh = create_refresh_token(str(user.id))
    return AuthResponse(access_token=access, refresh_token=refresh, user=UserBrief.model_validate(user))


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    access = create_access_token(str(user.id), {"tenant_id": str(user.tenant_id), "role": user.role})
    refresh = create_refresh_token(str(user.id))
    return AuthResponse(access_token=access, refresh_token=refresh, user=UserBrief.model_validate(user))
