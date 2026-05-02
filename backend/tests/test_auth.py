import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user: dict, user_password: str):
    response = await client.post(
        "/api/auth/login",
        data={
            "username": test_user["username"],
            "password": user_password,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_failure(client: AsyncClient, test_user: dict):
    response = await client.post(
        "/api/auth/login",
        data={
            "username": test_user["username"],
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

@pytest.mark.asyncio
async def test_get_me(auth_client: AsyncClient, test_user: dict):
    response = await auth_client.get("/api/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["id"] == test_user["id"]

@pytest.mark.asyncio
async def test_get_me_unauthorized(client: AsyncClient):
    response = await client.get("/api/auth/me")
    assert response.status_code == 401
