import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_add_reminder(auth_client: AsyncClient, test_service_item: dict):
    item_id = test_service_item["id"]
    response = await auth_client.post(
        "/api/reminders",
        json={
            "service_item_id": item_id,
            "interval_km": 10000,
            "interval_days": 365,
            "notify_before_km": 1000,
            "notify_before_days": 30,
            "note": "Use 5W-30 oil",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["interval_km"] == 10000
    assert data["note"] == "Use 5W-30 oil"


@pytest.mark.asyncio
async def test_add_reminder_validation_fail(
    auth_client: AsyncClient, test_service_item: dict
):
    item_id = test_service_item["id"]

    # Fail: notify_before_km > interval_km
    response = await auth_client.post(
        "/api/reminders",
        json={
            "service_item_id": item_id,
            "interval_km": 1000,
            "notify_before_km": 1500,  # Too much
        },
    )
    assert response.status_code == 422

    # Fail: notify_before_days without interval_days
    response = await auth_client.post(
        "/api/reminders",
        json={
            "service_item_id": item_id,
            "interval_km": 10000,
            "notify_before_days": 30,  # interval_days is missing
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_reminders(auth_client: AsyncClient, test_service_item: dict):
    item_id = test_service_item["id"]
    await auth_client.post(
        "/api/reminders",
        json={"service_item_id": item_id, "interval_km": 5000},
    )

    response = await auth_client.get(f"/api/reminders/service-item/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["interval_km"] == 5000


@pytest.mark.asyncio
async def test_update_reminder(auth_client: AsyncClient, test_service_item: dict):
    item_id = test_service_item["id"]
    create_resp = await auth_client.post(
        "/api/reminders",
        json={"service_item_id": item_id, "interval_km": 5000},
    )
    rem_id = create_resp.json()["id"]

    response = await auth_client.patch(
        f"/api/reminders/{rem_id}", json={"interval_km": 7500, "note": "Updated note"}
    )
    assert response.status_code == 200
    assert response.json()["interval_km"] == 7500
    assert response.json()["note"] == "Updated note"


@pytest.mark.asyncio
async def test_delete_reminder(auth_client: AsyncClient, test_service_item: dict):
    item_id = test_service_item["id"]
    create_resp = await auth_client.post(
        "/api/reminders",
        json={"service_item_id": item_id, "interval_km": 5000},
    )
    rem_id = create_resp.json()["id"]

    response = await auth_client.delete(f"/api/reminders/{rem_id}")
    assert response.status_code == 204

    get_resp = await auth_client.get(f"/api/reminders/{rem_id}")
    assert get_resp.status_code == 404
