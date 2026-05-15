"""Test Supabase Storage integration."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


def test_get_public_url_without_supabase():
    """When Supabase is not configured, returns local placeholder path."""
    from app.services.storage_service import get_public_url

    with patch("app.services.storage_service.settings") as mock_settings:
        mock_settings.SUPABASE_URL = ""
        result = get_public_url("evidence/abc/file.pdf")
    assert result == "/uploads/evidence/abc/file.pdf"


def test_get_public_url_with_supabase():
    from app.services.storage_service import get_public_url

    with patch("app.services.storage_service.settings") as mock_settings:
        mock_settings.SUPABASE_URL = "https://example.supabase.co"
        mock_settings.SUPABASE_STORAGE_BUCKET = "law-files"
        result = get_public_url("evidence/abc/file.pdf")
    assert result == "https://example.supabase.co/storage/v1/object/public/law-files/evidence/abc/file.pdf"


@pytest.mark.asyncio
async def test_upload_file_without_supabase():
    """When Supabase is not configured, returns local placeholder path."""
    from app.services.storage_service import upload_file

    with patch("app.services.storage_service.settings") as mock_settings:
        mock_settings.SUPABASE_URL = ""
        mock_settings.SUPABASE_SERVICE_ROLE_KEY = ""
        result = await upload_file(b"content", "test/file.pdf")
    assert result == "/uploads/test/file.pdf"


@pytest.mark.asyncio
async def test_upload_file_with_supabase_success():
    from app.services.storage_service import upload_file

    mock_resp = MagicMock()
    mock_resp.status_code = 200

    with patch("app.services.storage_service.settings") as mock_settings, \
         patch("httpx.AsyncClient") as mock_client_cls:
        mock_settings.SUPABASE_URL = "https://example.supabase.co"
        mock_settings.SUPABASE_SERVICE_ROLE_KEY = "test-key"
        mock_settings.SUPABASE_STORAGE_BUCKET = "law-files"

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_resp)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = await upload_file(b"content", "test/file.pdf", "application/pdf")

    assert "example.supabase.co" in result
    assert "test/file.pdf" in result
    mock_client.post.assert_called_once()


@pytest.mark.asyncio
async def test_upload_file_with_supabase_failure():
    from app.services.storage_service import upload_file

    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_resp.text = "Forbidden"

    with patch("app.services.storage_service.settings") as mock_settings, \
         patch("httpx.AsyncClient") as mock_client_cls:
        mock_settings.SUPABASE_URL = "https://example.supabase.co"
        mock_settings.SUPABASE_SERVICE_ROLE_KEY = "test-key"
        mock_settings.SUPABASE_STORAGE_BUCKET = "law-files"

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_resp)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        with pytest.raises(RuntimeError, match="Supabase upload failed"):
            await upload_file(b"content", "test/file.pdf")


@pytest.mark.asyncio
async def test_delete_file_without_supabase():
    from app.services.storage_service import delete_file

    with patch("app.services.storage_service.settings") as mock_settings:
        mock_settings.SUPABASE_URL = ""
        mock_settings.SUPABASE_SERVICE_ROLE_KEY = ""
        result = await delete_file("test/file.pdf")
    assert result is True  # No-op


@pytest.mark.asyncio
async def test_delete_file_with_supabase():
    from app.services.storage_service import delete_file

    mock_resp = MagicMock()
    mock_resp.status_code = 200

    with patch("app.services.storage_service.settings") as mock_settings, \
         patch("httpx.AsyncClient") as mock_client_cls:
        mock_settings.SUPABASE_URL = "https://example.supabase.co"
        mock_settings.SUPABASE_SERVICE_ROLE_KEY = "test-key"
        mock_settings.SUPABASE_STORAGE_BUCKET = "law-files"

        mock_client = AsyncMock()
        mock_client.delete = AsyncMock(return_value=mock_resp)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = await delete_file("test/file.pdf")
    assert result is True
