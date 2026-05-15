"""Supabase Storage integration for file uploads."""
from __future__ import annotations

import httpx

from app.core.config import settings


async def upload_file(
    file_content: bytes,
    path: str,
    content_type: str | None = None,
) -> str:
    """Upload a file to Supabase Storage and return the public URL.

    Falls back to a local path if Supabase is not configured.
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        # Supabase not configured — return a placeholder path
        return f"/uploads/{path}"

    bucket = settings.SUPABASE_STORAGE_BUCKET
    url = f"{settings.SUPABASE_URL}/storage/v1/object/{bucket}/{path}"

    headers = {
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
        "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
    }
    if content_type:
        headers["Content-Type"] = content_type

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, content=file_content, headers=headers)
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Supabase upload failed: {resp.status_code} {resp.text}")

    return get_public_url(path)


def get_public_url(path: str) -> str:
    """Get the public URL for a file in Supabase Storage."""
    if not settings.SUPABASE_URL:
        return f"/uploads/{path}"
    bucket = settings.SUPABASE_STORAGE_BUCKET
    return f"{settings.SUPABASE_URL}/storage/v1/object/public/{bucket}/{path}"


async def delete_file(path: str) -> bool:
    """Delete a file from Supabase Storage. Returns True if successful."""
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        return True  # No-op when unconfigured

    bucket = settings.SUPABASE_STORAGE_BUCKET
    url = f"{settings.SUPABASE_URL}/storage/v1/object/{bucket}/{path}"

    headers = {
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
        "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.delete(url, headers=headers)
        return resp.status_code in (200, 204, 404)
