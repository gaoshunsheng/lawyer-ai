from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.favorite import FavoriteCreate, FavoriteResponse, FavoriteUpdate
from app.services import favorite_service

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("", response_model=list[FavoriteResponse])
async def list_favorites(
    target_type: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await favorite_service.list_favorites(db, current_user.id, target_type)
    return [FavoriteResponse.model_validate(i) for i in items]


@router.post("", response_model=FavoriteResponse, status_code=201)
async def create_favorite(
    req: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    already = await favorite_service.is_favorited(db, current_user.id, req.target_type, req.target_id)
    if already:
        raise HTTPException(status_code=409, detail="已收藏")
    try:
        fav = await favorite_service.create_favorite(db, current_user.id, req.model_dump())
    except Exception as exc:
        from sqlalchemy.exc import IntegrityError
        if isinstance(exc, IntegrityError):
            raise HTTPException(status_code=409, detail="已收藏")
        raise
    return FavoriteResponse.model_validate(fav)


@router.put("/{favorite_id}", response_model=FavoriteResponse)
async def update_favorite(
    favorite_id: uuid.UUID,
    req: FavoriteUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    fav = await favorite_service.get_favorite(db, favorite_id)
    if not fav or fav.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="收藏不存在")
    fav = await favorite_service.update_favorite(db, fav, req.model_dump(exclude_unset=True))
    return FavoriteResponse.model_validate(fav)


@router.delete("/{favorite_id}", status_code=204)
async def delete_favorite(
    favorite_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    fav = await favorite_service.get_favorite(db, favorite_id)
    if not fav or fav.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="收藏不存在")
    await favorite_service.delete_favorite(db, fav)
    return None
