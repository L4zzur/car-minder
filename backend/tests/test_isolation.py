import uuid
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.fixture
async def second_user(client: AsyncClient, user_password: str) -> dict:
    """Fixture to create a second independent user."""
    unique_username = f"user_b_{uuid.uuid4().hex[:8]}"
    response = await client.post(
        "/api/users",
        json={
            "username": unique_username,
            "name": "Second User",
            "password": user_password,
        },
    )
    return response.json()


@pytest.fixture
async def second_auth_client(
    client: AsyncClient, second_user: dict, user_password: str
) -> AsyncGenerator[AsyncClient]:
    """Fixture providing an HTTP client authenticated as User B."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as login_client:
        login_resp = await login_client.post(
            "/api/auth/login",
            data={
                "username": second_user["username"],
                "password": user_password,
            },
        )
        token = login_resp.json()["access_token"]

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"Authorization": f"Bearer {token}"},
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_user_cannot_access_other_user_car(
    auth_client: AsyncClient,
    second_auth_client: AsyncClient,
    test_car: dict,
):
    """User B must not be able to get, update, or delete User A's car."""
    car_id = test_car["id"]

    # Get
    resp = await second_auth_client.get(f"/api/cars/{car_id}")
    assert resp.status_code == 404

    # Update
    resp = await second_auth_client.patch(
        f"/api/cars/{car_id}",
        json={"brand": "Hacked"},
    )
    assert resp.status_code == 404

    # Delete
    resp = await second_auth_client.delete(f"/api/cars/{car_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_user_cannot_add_mileage_log_to_other_user_car(
    auth_client: AsyncClient,
    second_auth_client: AsyncClient,
    test_car: dict,
):
    """User B must not be able to post mileage logs or list logs for User A's car."""
    car_id = test_car["id"]

    # Post log to User A's car
    resp = await second_auth_client.post(
        "/api/mileage-logs",
        json={"car_id": car_id, "odometer_km": 99999},
    )
    assert resp.status_code == 404
    assert resp.json()["code"] == "car_not_found"

    # List logs for User A's car
    resp = await second_auth_client.get(f"/api/mileage-logs?car_id={car_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_user_cannot_access_other_user_service_items(
    auth_client: AsyncClient,
    second_auth_client: AsyncClient,
    test_service_item: dict,
    test_car: dict,
):
    """User B must not be able to view, mark serviced, delete User A's service item, or add item to User A's car."""
    item_id = test_service_item["id"]
    car_id = test_car["id"]

    # Get
    resp = await second_auth_client.get(f"/api/service-items/{item_id}")
    assert resp.status_code == 404

    # Mark serviced
    resp = await second_auth_client.post(
        f"/api/service-items/{item_id}/mark-serviced",
        json={"serviced_at": "2026-02-01T00:00:00Z", "odometer_km": 1500},
    )
    assert resp.status_code == 404

    # Delete
    resp = await second_auth_client.delete(f"/api/service-items/{item_id}")
    assert resp.status_code == 404

    # Create service item on User A's car
    resp = await second_auth_client.post(
        "/api/service-items",
        json={
            "car_id": car_id,
            "name": "Malicious Service Item",
            "last_service_at": "2026-01-01T00:00:00Z",
            "last_service_odometer_km": 1000,
        },
    )
    assert resp.status_code == 404
    assert resp.json()["code"] == "car_not_found"


@pytest.mark.asyncio
async def test_user_cannot_access_other_user_reminders(
    auth_client: AsyncClient,
    second_auth_client: AsyncClient,
    test_service_item: dict,
):
    """User B must not be able to add, get, or delete reminders for User A's service item."""
    item_id = test_service_item["id"]

    # User A creates a reminder
    create_resp = await auth_client.post(
        "/api/reminders",
        json={
            "service_item_id": item_id,
            "interval_km": 10000,
            "notify_before_km": 1000,
        },
    )
    assert create_resp.status_code == 201
    reminder_id = create_resp.json()["id"]

    # User B tries to get User A's reminder
    resp = await second_auth_client.get(f"/api/reminders/{reminder_id}")
    assert resp.status_code == 404

    # User B tries to delete User A's reminder
    resp = await second_auth_client.delete(f"/api/reminders/{reminder_id}")
    assert resp.status_code == 404

    # User B tries to create a reminder on User A's service item
    resp = await second_auth_client.post(
        "/api/reminders",
        json={
            "service_item_id": item_id,
            "interval_km": 5000,
            "notify_before_km": 500,
        },
    )
    assert resp.status_code == 404
    assert resp.json()["code"] == "service_item_not_found"
