import time
import pytest
from httpx import AsyncClient

# These tests require a running DB and share the asyncpg engine across tests.
# They may fail due to event-loop conflicts with pytest-asyncio.
# Mark them as integration tests so they can be skipped in CI if needed.


@pytest.mark.asyncio
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
