import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models import ModelConfig, User
from app.schemas.token_usage import ModelConfigResponse

router = APIRouter(prefix="/models", tags=["models"])


@router.get("/", response_model=list[ModelConfigResponse])
async def list_models(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ModelConfig)
        .where(ModelConfig.status == "active")
        .order_by(ModelConfig.is_default.desc())
    )
    return result.scalars().all()


@router.get("/{model_id}", response_model=ModelConfigResponse)
async def get_model(
    model_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("platform_admin", "tenant_admin")),
):
    result = await db.execute(select(ModelConfig).where(ModelConfig.id == model_id))
    model = result.scalar_one_or_none()
    if not model:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="模型配置不存在")
    return model
