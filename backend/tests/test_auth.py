import time
import pytest
from httpx import AsyncClient

# These tests require a running PostgreSQL database.
# They are skipped automatically if the DB is not reachable.


def _check_db():
    """Check if PostgreSQL is reachable."""
    import socket
    try:
        s = socket.create_connection(("127.0.0.1", 5432), timeout=1)
        s.close()
        return True
    except OSError:
        return False


requires_db = pytest.mark.skipif(not _check_db(), reason="PostgreSQL not running")


@pytest.mark.asyncio
@requires_db
async def test_register(client: AsyncClient):
    unique = f"testlawyer_{int(time.time())}"
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": unique,
            "email": f"{unique}@example.com",
            "password": "Test123456!",
            "real_name": "测试律师",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["username"] == unique


@pytest.mark.asyncio
@requires_db
async def test_login(client: AsyncClient):
    unique = f"loginuser_{int(time.time())}"
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "username": unique,
            "email": f"{unique}@example.com",
            "password": "Test123456!",
            "real_name": "测试律师",
        },
    )
    assert reg.status_code == 201, f"Register failed: {reg.text}"
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": unique, "password": "Test123456!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
@requires_db
async def test_login_wrong_password(client: AsyncClient):
    unique = f"wrongpw_{int(time.time())}"
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "username": unique,
            "email": f"{unique}@example.com",
            "password": "Test123456!",
            "real_name": "测试律师",
        },
    )
    assert reg.status_code == 201, f"Register failed: {reg.text}"
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": unique, "password": "wrong"},
    )
    assert response.status_code == 401
