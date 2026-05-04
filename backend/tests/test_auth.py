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
    assert "access_token" in response.cookies
    assert "csrf_token" in response.cookies


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
async def test_get_me_with_cookie_auth(
    cookie_auth_client: AsyncClient,
    test_user: dict,
):
    response = await cookie_auth_client.get("/api/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["id"] == test_user["id"]


@pytest.mark.asyncio
async def test_get_me_unauthorized(client: AsyncClient):
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_invalid_bearer_token(client: AsyncClient):
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_cookie_auth_requires_csrf_for_unsafe_methods(
    cookie_auth_client: AsyncClient,
):
    response = await cookie_auth_client.post(
        "/api/cars",
        json={
            "brand": "No",
            "model": "Csrf",
            "year": 2020,
            "initial_odometer_km": 1000,
        },
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_cookie_auth_accepts_valid_csrf_for_unsafe_methods(
    cookie_auth_client: AsyncClient,
):
    csrf_token = cookie_auth_client.cookies["csrf_token"]
    response = await cookie_auth_client.post(
        "/api/cars",
        headers={"X-CSRF-Token": csrf_token},
        json={
            "brand": "With",
            "model": "Csrf",
            "year": 2020,
            "initial_odometer_km": 1000,
        },
    )
    assert response.status_code == 201
