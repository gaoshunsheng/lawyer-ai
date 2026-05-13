import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "testlawyer",
            "email": "test@example.com",
            "password": "Test123456!",
            "real_name": "测试律师",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["username"] == "testlawyer"


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "testlawyer", "password": "Test123456!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "testlawyer", "password": "wrong"},
    )
    assert response.status_code == 401
