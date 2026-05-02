import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_add_car(auth_client: AsyncClient, test_user: dict):
    response = await auth_client.post(
        "/api/cars",
        json={
            "brand": "Volkswagen",
            "model": "Golf",
            "year": 2020,
            "initial_odometer_km": 15000,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["brand"] == "Volkswagen"
    assert data["user_id"] == test_user["id"]
    assert "id" in data


@pytest.mark.asyncio
async def test_get_car(auth_client: AsyncClient, test_user: dict):
    # Add a car first
    create_resp = await auth_client.post(
        "/api/cars",
        json={
            "brand": "Kia",
            "model": "Soul",
            "year": 2022,
            "initial_odometer_km": 5000,
        },
    )
    car_id = create_resp.json()["id"]

    # Get by ID
    response = await auth_client.get(f"/api/cars/{car_id}")
    assert response.status_code == 200
    assert response.json()["brand"] == "Kia"


@pytest.mark.asyncio
async def test_get_car_unauthorized(client: AsyncClient, auth_client: AsyncClient):
    # Add a car with one user
    create_resp = await auth_client.post(
        "/api/cars",
        json={
            "brand": "Secret",
            "model": "Car",
            "year": 2022,
            "initial_odometer_km": 5000,
        },
    )
    car_id = create_resp.json()["id"]

    # Try to get with NO user
    response = await client.get(f"/api/cars/{car_id}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_user_cars(auth_client: AsyncClient):
    await auth_client.post(
        "/api/cars",
        json={
            "brand": "Ford",
            "model": "F-150",
            "year": 2019,
            "initial_odometer_km": 40000,
        },
    )

    response = await auth_client.get("/api/cars")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(car["brand"] == "Ford" for car in data)


@pytest.mark.asyncio
async def test_update_car(auth_client: AsyncClient):
    create_resp = await auth_client.post(
        "/api/cars",
        json={
            "brand": "Tesla",
            "model": "Model 3",
            "year": 2021,
            "initial_odometer_km": 0,
        },
    )
    car_id = create_resp.json()["id"]

    response = await auth_client.patch(
        f"/api/cars/{car_id}", json={"model": "Model Y", "year": 2023}
    )
    assert response.status_code == 200
    assert response.json()["model"] == "Model Y"
    assert response.json()["year"] == 2023


@pytest.mark.asyncio
async def test_delete_car(auth_client: AsyncClient):
    create_resp = await auth_client.post(
        "/api/cars",
        json={
            "brand": "Toyota",
            "model": "Yaris",
            "year": 2018,
            "initial_odometer_km": 60000,
        },
    )
    car_id = create_resp.json()["id"]

    response = await auth_client.delete(f"/api/cars/{car_id}")
    assert response.status_code == 204

    get_resp = await auth_client.get(f"/api/cars/{car_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_add_car_future_year(auth_client: AsyncClient):
    import datetime

    future_year = datetime.datetime.now().year + 1
    response = await auth_client.post(
        "/api/cars",
        json={
            "brand": "FutureCar",
            "model": "X",
            "year": future_year,
            "initial_odometer_km": 0,
        },
    )
    assert response.status_code == 422
