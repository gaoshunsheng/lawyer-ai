import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from pydantic import ValidationError

from app.services import favorite_service
from app.schemas.favorite import FavoriteCreate, FavoriteUpdate, FavoriteResponse


# ── Schema tests ──

def test_favorite_create_requires_target_type():
    with pytest.raises(ValidationError):
        FavoriteCreate(target_id=uuid.uuid4())


def test_favorite_create_requires_target_id():
    with pytest.raises(ValidationError):
        FavoriteCreate(target_type="law")


def test_favorite_create_with_notes():
    req = FavoriteCreate(target_type="law", target_id=uuid.uuid4(), notes="重要法规")
    assert req.notes == "重要法规"


def test_favorite_create_without_notes():
    req = FavoriteCreate(target_type="law", target_id=uuid.uuid4())
    assert req.notes is None


def test_favorite_update_all_optional():
    req = FavoriteUpdate()
    assert req.notes is None


def test_favorite_update_with_notes():
    req = FavoriteUpdate(notes="更新笔记")
    assert req.notes == "更新笔记"


# ── Service tests ──

@pytest.mark.asyncio
async def test_is_favorited_returns_true():
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar.return_value = 1
    mock_db.execute.return_value = mock_result

    result = await favorite_service.is_favorited(
        mock_db, uuid.uuid4(), "law", uuid.uuid4()
    )
    assert result is True


@pytest.mark.asyncio
async def test_is_favorited_returns_false():
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar.return_value = 0
    mock_db.execute.return_value = mock_result

    result = await favorite_service.is_favorited(
        mock_db, uuid.uuid4(), "law", uuid.uuid4()
    )
    assert result is False


@pytest.mark.asyncio
async def test_create_favorite():
    mock_db = AsyncMock()
    user_id = uuid.uuid4()
    data = {"target_type": "law", "target_id": uuid.uuid4()}

    result = await favorite_service.create_favorite(mock_db, user_id, data)
    mock_db.add.assert_called_once()
    mock_db.flush.assert_called_once()


@pytest.mark.asyncio
async def test_delete_favorite():
    from app.models.favorite import Favorite

    mock_db = AsyncMock()
    fav = Favorite(user_id=uuid.uuid4(), target_type="law", target_id=uuid.uuid4())

    await favorite_service.delete_favorite(mock_db, fav)
    mock_db.delete.assert_called_once_with(fav)


@pytest.mark.asyncio
async def test_update_favorite_notes():
    from app.models.favorite import Favorite

    mock_db = AsyncMock()
    fav = Favorite(user_id=uuid.uuid4(), target_type="law", target_id=uuid.uuid4())

    await favorite_service.update_favorite(mock_db, fav, {"notes": "更新笔记"})
    assert fav.notes == "更新笔记"
    mock_db.flush.assert_called_once()


@pytest.mark.asyncio
async def test_get_favorite_found():
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = "a_favorite"
    mock_db.execute.return_value = mock_result

    result = await favorite_service.get_favorite(mock_db, uuid.uuid4())
    assert result == "a_favorite"


@pytest.mark.asyncio
async def test_get_favorite_not_found():
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    result = await favorite_service.get_favorite(mock_db, uuid.uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_list_favorites():
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = ["fav1", "fav2"]
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_result

    result = await favorite_service.list_favorites(mock_db, uuid.uuid4())
    assert result == ["fav1", "fav2"]


@pytest.mark.asyncio
async def test_list_favorites_with_target_type_filter():
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_result

    result = await favorite_service.list_favorites(
        mock_db, uuid.uuid4(), target_type="case"
    )
    assert result == []
