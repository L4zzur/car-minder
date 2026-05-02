import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_add_mileage_log(auth_client: AsyncClient, test_car: dict):
    car_id = test_car["id"]
    initial_mileage = test_car["initial_odometer_km"]
    
    # Add new mileage (valid: > initial)
    response = await auth_client.post(
        "/api/mileage-logs",
        json={
            "car_id": car_id,
            "odometer_km": initial_mileage + 500
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["odometer_km"] == initial_mileage + 500
    assert data["car_id"] == car_id

@pytest.mark.asyncio
async def test_add_mileage_log_rollback_fail(auth_client: AsyncClient, test_car: dict):
    car_id = test_car["id"]
    initial_mileage = test_car["initial_odometer_km"]
    
    # Try to add mileage LESS than initial (invalid)
    response = await auth_client.post(
        "/api/mileage-logs",
        json={
            "car_id": car_id,
            "odometer_km": initial_mileage - 100
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "odometer_rollback"

@pytest.mark.asyncio
async def test_add_mileage_log_no_advance_fail(auth_client: AsyncClient, test_car: dict):
    car_id = test_car["id"]
    initial_mileage = test_car["initial_odometer_km"]
    
    # Try to add mileage EQUAL to initial (invalid for logs)
    response = await auth_client.post(
        "/api/mileage-logs",
        json={
            "car_id": car_id,
            "odometer_km": initial_mileage
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "odometer_not_advanced"

@pytest.mark.asyncio
async def test_list_mileage_logs(auth_client: AsyncClient, test_car: dict):
    car_id = test_car["id"]
    initial_mileage = test_car["initial_odometer_km"]
    
    # Add two logs
    await auth_client.post("/api/mileage-logs", json={"car_id": car_id, "odometer_km": initial_mileage + 100})
    await auth_client.post("/api/mileage-logs", json={"car_id": car_id, "odometer_km": initial_mileage + 200})
    
    response = await auth_client.get(f"/api/mileage-logs/car/{car_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(log["odometer_km"] == initial_mileage + 100 for log in data)
    assert any(log["odometer_km"] == initial_mileage + 200 for log in data)

@pytest.mark.asyncio
async def test_delete_mileage_log(auth_client: AsyncClient, test_car: dict):
    car_id = test_car["id"]
    initial_mileage = test_car["initial_odometer_km"]
    
    create_resp = await auth_client.post(
        "/api/mileage-logs",
        json={"car_id": car_id, "odometer_km": initial_mileage + 100}
    )
    log_id = create_resp.json()["id"]
    
    response = await auth_client.delete(f"/api/mileage-logs/{log_id}")
    assert response.status_code == 204
    
    # Verify deletion
    list_resp = await auth_client.get(f"/api/mileage-logs/car/{car_id}")
    data = list_resp.json()
    assert all(log["id"] != log_id for log in data)
