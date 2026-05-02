import pytest
from httpx import AsyncClient
from datetime import datetime, timezone

@pytest.mark.asyncio
async def test_add_service_item(auth_client: AsyncClient, test_car: dict):
    car_id = test_car["id"]
    now = datetime.now(timezone.utc).isoformat()
    
    response = await auth_client.post(
        "/api/service-items",
        json={
            "car_id": car_id,
            "name": "Engine Oil",
            "last_service_at": now,
            "last_service_odometer_km": 5000
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Engine Oil"
    assert data["last_service_odometer_km"] == 5000

@pytest.mark.asyncio
async def test_list_service_items(auth_client: AsyncClient, test_car: dict):
    car_id = test_car["id"]
    now = datetime.now(timezone.utc).isoformat()
    
    await auth_client.post(
        "/api/service-items",
        json={
            "car_id": car_id,
            "name": "Brake Pads",
            "last_service_at": now,
            "last_service_odometer_km": 10000
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
    now = datetime.now(timezone.utc).isoformat()
    
    # 1. Create service item
    create_resp = await auth_client.post(
        "/api/service-items",
        json={
            "car_id": car_id,
            "name": "Air Filter",
            "last_service_at": now,
            "last_service_odometer_km": initial_mileage
        },
    )
    item_id = create_resp.json()["id"]
    
    # 2. Mark as serviced with HIGHER mileage
    new_mileage = initial_mileage + 2000
    mark_resp = await auth_client.post(
        f"/api/service-items/{item_id}/mark-serviced",
        json={
            "serviced_at": now,
            "odometer_km": new_mileage
        }
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
    now = datetime.now(timezone.utc).isoformat()
    
    create_resp = await auth_client.post(
        "/api/service-items",
        json={
            "car_id": car_id,
            "name": "Spark Plugs",
            "last_service_at": now,
            "last_service_odometer_km": initial_mileage
        },
    )
    item_id = create_resp.json()["id"]
    
    # Try to mark serviced with mileage LOWER than current
    response = await auth_client.post(
        f"/api/service-items/{item_id}/mark-serviced",
        json={
            "serviced_at": now,
            "odometer_km": initial_mileage - 500
        }
    )
    assert response.status_code == 422
    assert response.json()["code"] == "odometer_rollback"

@pytest.mark.asyncio
async def test_delete_service_item(auth_client: AsyncClient, test_car: dict):
    car_id = test_car["id"]
    now = datetime.now(timezone.utc).isoformat()
    
    create_resp = await auth_client.post(
        "/api/service-items",
        json={
            "car_id": car_id,
            "name": "Temporary Item",
            "last_service_at": now,
            "last_service_odometer_km": 1000
        },
    )
    item_id = create_resp.json()["id"]
    
    response = await auth_client.delete(f"/api/service-items/{item_id}")
    assert response.status_code == 204
    
    # Verify it's gone
    get_resp = await auth_client.get(f"/api/service-items/{item_id}")
    assert get_resp.status_code == 404
