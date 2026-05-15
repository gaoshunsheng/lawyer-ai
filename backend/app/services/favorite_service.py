from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.favorite import Favorite


async def list_favorites(
    db: AsyncSession,
    user_id: uuid.UUID,
    target_type: str | None = None,
) -> list[Favorite]:
    conditions = [Favorite.user_id == user_id]
    if target_type:
        conditions.append(Favorite.target_type == target_type)
    stmt = select(Favorite).where(*conditions).order_by(Favorite.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_favorite(db: AsyncSession, favorite_id: uuid.UUID) -> Favorite | None:
    stmt = select(Favorite).where(Favorite.id == favorite_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_favorite(db: AsyncSession, user_id: uuid.UUID, data: dict) -> Favorite:
    fav = Favorite(user_id=user_id, **data)
    db.add(fav)
    await db.flush()
    return fav


async def update_favorite(db: AsyncSession, fav: Favorite, data: dict) -> Favorite:
    for key, value in data.items():
        if value is not None:
            setattr(fav, key, value)
    await db.flush()
    return fav


async def delete_favorite(db: AsyncSession, fav: Favorite) -> None:
    await db.delete(fav)
    await db.flush()


async def is_favorited(db: AsyncSession, user_id: uuid.UUID, target_type: str, target_id: uuid.UUID) -> bool:
    stmt = select(func.count(Favorite.id)).where(
        Favorite.user_id == user_id,
        Favorite.target_type == target_type,
        Favorite.target_id == target_id,
    )
    result = await db.execute(stmt)
    return (result.scalar() or 0) > 0
