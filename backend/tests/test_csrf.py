import pytest
from httpx import ASGITransport, AsyncClient

from api.routes.auth import ACCESS_TOKEN_COOKIE, CSRF_TOKEN_COOKIE
from main import app


@pytest.mark.asyncio
async def test_csrf_cookie_auth_without_csrf_header_fails(
    client: AsyncClient, test_user: dict, user_password: str
):
    """Cookie auth without X-CSRF-Token header should return 403 Forbidden."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        login_resp = await ac.post(
            "/api/auth/login",
            data={"username": test_user["username"], "password": user_password},
        )
        assert login_resp.status_code == 200

        # Unsafe POST without x-csrf-token header
        car_resp = await ac.post(
            "/api/cars",
            json={
                "brand": "Toyota",
                "model": "Camry",
                "year": 2022,
                "initial_odometer_km": 50000,
            },
        )
        assert car_resp.status_code == 403
        assert car_resp.json()["detail"] == "CSRF token missing or invalid"


@pytest.mark.asyncio
async def test_csrf_cookie_auth_with_mismatched_csrf_header_fails(
    client: AsyncClient, test_user: dict, user_password: str
):
    """Cookie auth with invalid X-CSRF-Token header should return 403 Forbidden."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        await ac.post(
            "/api/auth/login",
            data={"username": test_user["username"], "password": user_password},
        )

        car_resp = await ac.post(
            "/api/cars",
            json={
                "brand": "Toyota",
                "model": "Camry",
                "year": 2022,
                "initial_odometer_km": 50000,
            },
            headers={"x-csrf-token": "completely_wrong_csrf_token"},
        )
        assert car_resp.status_code == 403
        assert car_resp.json()["detail"] == "CSRF token missing or invalid"


@pytest.mark.asyncio
async def test_csrf_cookie_auth_with_valid_csrf_header_succeeds(
    client: AsyncClient, test_user: dict, user_password: str
):
    """Cookie auth with matching X-CSRF-Token header should succeed."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        await ac.post(
            "/api/auth/login",
            data={"username": test_user["username"], "password": user_password},
        )

        csrf_cookie = ac.cookies.get(CSRF_TOKEN_COOKIE)
        assert csrf_cookie is not None

        car_resp = await ac.post(
            "/api/cars",
            json={
                "brand": "Toyota",
                "model": "Camry",
                "year": 2022,
                "initial_odometer_km": 50000,
            },
            headers={"x-csrf-token": csrf_cookie},
        )
        assert car_resp.status_code == 201
        assert car_resp.json()["brand"] == "Toyota"


@pytest.mark.asyncio
async def test_csrf_safe_methods_exempt(
    client: AsyncClient, test_user: dict, user_password: str
):
    """GET requests with cookies but without X-CSRF-Token should succeed."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        await ac.post(
            "/api/auth/login",
            data={"username": test_user["username"], "password": user_password},
        )

        cars_resp = await ac.get("/api/cars")
        assert cars_resp.status_code == 200


@pytest.mark.asyncio
async def test_csrf_bearer_auth_exempt(auth_client: AsyncClient):
    """Bearer token authentication should not be blocked by CSRF middleware."""
    car_resp = await auth_client.post(
        "/api/cars",
        json={
            "brand": "BMW",
            "model": "X5",
            "year": 2021,
            "initial_odometer_km": 30000,
        },
    )
    assert car_resp.status_code == 201
    assert car_resp.json()["brand"] == "BMW"


@pytest.mark.asyncio
async def test_csrf_exempt_registration_endpoint(client: AsyncClient):
    """POST /api/users (registration) is exempt from CSRF checks."""
    resp = await client.post(
        "/api/users",
        json={
            "username": "exempt_user_test",
            "name": "Exempt Test",
            "password": "password123",
        },
    )
    assert resp.status_code == 201
