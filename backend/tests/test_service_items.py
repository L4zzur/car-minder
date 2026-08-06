from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_add_service_item(auth_client: AsyncClient, test_car: dict):
    car_id = test_car["id"]
    now = datetime.now(UTC).isoformat()

    response = await auth_client.post(
        "/api/service-items",
        json={
            "car_id": car_id,
            "name": "Engine Oil",
            "last_service_at": now,
            "last_service_odometer_km": 5000,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Engine Oil"
    assert data["last_service_odometer_km"] == 5000


@pytest.mark.asyncio
async def test_list_service_items(auth_client: AsyncClient, test_car: dict):
    car_id = test_car["id"]
    now = datetime.now(UTC).isoformat()

    await auth_client.post(
        "/api/service-items",
        json={
            "car_id": car_id,
            "name": "Brake Pads",
            "last_service_at": now,
            "last_service_odometer_km": 10000,
        },
    )

    response = await auth_client.get(f"/api/service-items/car/{car_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(item["name"] == "Brake Pads" for item in data)


@pytest.mark.asyncio
async def test_mark_serviced_updates_mileage(auth_client: AsyncClient, test_car: dict):
    car_id = test_car["id"]
    initial_mileage = test_car["initial_odometer_km"]
    now = datetime.now(UTC).isoformat()

    # 1. Create service item
    create_resp = await auth_client.post(
        "/api/service-items",
        json={
            "car_id": car_id,
            "name": "Air Filter",
            "last_service_at": now,
            "last_service_odometer_km": initial_mileage,
        },
    )
    item_id = create_resp.json()["id"]

    # 2. Mark as serviced with HIGHER mileage
    new_mileage = initial_mileage + 2000
    mark_resp = await auth_client.post(
        f"/api/service-items/{item_id}/mark-serviced",
        json={"serviced_at": now, "odometer_km": new_mileage},
    )
    assert mark_resp.status_code == 200
    assert mark_resp.json()["last_service_odometer_km"] == new_mileage

    # 3. Verify that a mileage log was automatically created
    mileage_resp = await auth_client.get(f"/api/mileage-logs/car/{car_id}")
    mileage_data = mileage_resp.json()
    assert any(log["odometer_km"] == new_mileage for log in mileage_data)


@pytest.mark.asyncio
async def test_mark_serviced_rollback_fail(auth_client: AsyncClient, test_car: dict):
    car_id = test_car["id"]
    initial_mileage = test_car["initial_odometer_km"]
    now = datetime.now(UTC).isoformat()

    create_resp = await auth_client.post(
        "/api/service-items",
        json={
            "car_id": car_id,
            "name": "Spark Plugs",
            "last_service_at": now,
            "last_service_odometer_km": initial_mileage,
        },
    )
    item_id = create_resp.json()["id"]

    # Try to mark serviced with mileage LOWER than current
    response = await auth_client.post(
        f"/api/service-items/{item_id}/mark-serviced",
        json={"serviced_at": now, "odometer_km": initial_mileage - 500},
    )
    assert response.status_code == 422
    assert response.json()["code"] == "odometer_rollback"


@pytest.mark.asyncio
async def test_delete_service_item(auth_client: AsyncClient, test_car: dict):
    car_id = test_car["id"]
    now = datetime.now(UTC).isoformat()

    create_resp = await auth_client.post(
        "/api/service-items",
        json={
            "car_id": car_id,
            "name": "Temporary Item",
            "last_service_at": now,
            "last_service_odometer_km": 1000,
        },
    )
    item_id = create_resp.json()["id"]

    response = await auth_client.delete(f"/api/service-items/{item_id}")
    assert response.status_code == 204

    # Verify it's gone
    get_resp = await auth_client.get(f"/api/service-items/{item_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_status_no_reminders(auth_client: AsyncClient, test_car: dict):
    # No reminders, status ok
    car_id = test_car["id"]
    now = datetime.now(UTC).isoformat()

    await auth_client.post(
        "/api/service-items",
        json={
            "car_id": car_id,
            "name": "No Reminder Item",
            "last_service_at": now,
            "last_service_odometer_km": 1000,
        },
    )

    response = await auth_client.get(f"/api/service-items/car/{car_id}")
    items = response.json()
    item = next(i for i in items if i["name"] == "No Reminder Item")

    assert item["status"] == "ok"
    assert item["km_until_due"] is None
    assert item["days_until_due"] is None


@pytest.mark.asyncio
async def test_status_km_due(auth_client: AsyncClient, test_car: dict):
    # Mileage status due
    car_id = test_car["id"]
    now = datetime.now(UTC).isoformat()

    # ServiceIetm: last service at 1000 km
    create_resp = await auth_client.post(
        "/api/service-items",
        json={
            "car_id": car_id,
            "name": "Oil Due",
            "last_service_at": now,
            "last_service_odometer_km": 1000,
        },
    )
    item_id = create_resp.json()["id"]

    # Reminder: interval 5000 km, notify at 0
    await auth_client.post(
        "/api/reminders",
        json={
            "service_item_id": item_id,
            "interval_km": 5000,
            "notify_before_km": 0,
        },
    )

    # Increase the mileage to 6500 (service was due at 6000 -> overdue by 500)
    await auth_client.post(
        "/api/mileage-logs",
        json={"car_id": car_id, "odometer_km": 6500},
    )

    response = await auth_client.get(f"/api/service-items/car/{car_id}")
    items = response.json()
    item = next(i for i in items if i["name"] == "Oil Due")

    assert item["status"] == "due"
    assert item["km_until_due"] == -500


@pytest.mark.asyncio
async def test_status_priority_due_over_ok(auth_client: AsyncClient, test_car: dict):
    # If one reminder is ok and the other is due -> overall status is due
    car_id = test_car["id"]
    two_days_ago = (datetime.now(UTC) - timedelta(days=2)).isoformat()

    create_resp = await auth_client.post(
        "/api/service-items",
        json={
            "car_id": car_id,
            "name": "Multi Reminder",
            "last_service_at": two_days_ago,
            "last_service_odometer_km": 1000,
        },
    )
    item_id = create_resp.json()["id"]

    # Mileage reminder - still far from service (ok)
    await auth_client.post(
        "/api/reminders",
        json={
            "service_item_id": item_id,
            "interval_km": 50000,
            "notify_before_km": 0,
        },
    )

    # Day reminder — overdue (due, interval 1 day, serviced 2 days ago)
    await auth_client.post(
        "/api/reminders",
        json={
            "service_item_id": item_id,
            "interval_days": 1,
            "notify_before_days": 0,
        },
    )

    response = await auth_client.get(f"/api/service-items/car/{car_id}")
    items = response.json()
    item = next(i for i in items if i["name"] == "Multi Reminder")

    assert item["status"] == "due"
    assert item["days_until_due"] is not None
    assert item["days_until_due"] <= 0


@pytest.mark.asyncio
async def test_status_soon_km(auth_client: AsyncClient, test_car: dict):
    # Service item: last service at 1000 km, initial car km = 1000
    car_id = test_car["id"]
    now = datetime.now(UTC).isoformat()

    create_resp = await auth_client.post(
        "/api/service-items",
        json={
            "car_id": car_id,
            "name": "Soon KM Item",
            "last_service_at": now,
            "last_service_odometer_km": 1000,
        },
    )
    item_id = create_resp.json()["id"]

    # Interval: 5000 km (due at 6000 km). Notify before: 1000 km (notify at 5000 km).
    await auth_client.post(
        "/api/reminders",
        json={
            "service_item_id": item_id,
            "interval_km": 5000,
            "notify_before_km": 1000,
        },
    )

    # Set odometer to 5200 (between 5000 and 6000) -> status should be "soon"
    await auth_client.post(
        "/api/mileage-logs",
        json={"car_id": car_id, "odometer_km": 5200},
    )

    response = await auth_client.get(f"/api/service-items/car/{car_id}")
    items = response.json()
    item = next(i for i in items if i["name"] == "Soon KM Item")

    assert item["status"] == "soon"
    assert item["km_until_due"] == 800


@pytest.mark.asyncio
async def test_status_soon_days(auth_client: AsyncClient, test_car: dict):
    # Service item: serviced 25 days ago (plus 1 hour buffer so fractional seconds don't drop .days to 4)
    car_id = test_car["id"]
    twenty_five_days_ago = (
        datetime.now(UTC) - timedelta(days=25) + timedelta(hours=1)
    ).isoformat()

    create_resp = await auth_client.post(
        "/api/service-items",
        json={
            "car_id": car_id,
            "name": "Soon Days Item",
            "last_service_at": twenty_five_days_ago,
            "last_service_odometer_km": 1000,
        },
    )
    item_id = create_resp.json()["id"]

    # Interval: 30 days (due in 5 days). Notify before: 10 days (notify starting 20 days after service)
    await auth_client.post(
        "/api/reminders",
        json={
            "service_item_id": item_id,
            "interval_days": 30,
            "notify_before_days": 10,
        },
    )

    response = await auth_client.get(f"/api/service-items/car/{car_id}")
    items = response.json()
    item = next(i for i in items if i["name"] == "Soon Days Item")

    assert item["status"] == "soon"
    assert item["days_until_due"] == 5


@pytest.mark.asyncio
async def test_service_item_not_found(auth_client: AsyncClient):
    import uuid

    fake_id = str(uuid.uuid4())
    resp = await auth_client.get(f"/api/service-items/{fake_id}")
    assert resp.status_code == 404

    resp = await auth_client.delete(f"/api/service-items/{fake_id}")
    assert resp.status_code == 404

