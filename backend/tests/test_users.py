import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    # Create a user
    response = await client.post(
        "/api/users",
        json={
            "username": "aceaura",
            "name": "Ace Aura",
            "password": "securepassword123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "aceaura"
    assert data["name"] == "Ace Aura"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_user_by_username(client: AsyncClient):
    # Create a user
    await client.post(
        "/api/users",
        json={
            "username": "dodgefuski",
            "name": "Dodge & Fuski",
            "password": "securepassword123",
        },
    )

    # Get user by username
    response = await client.get("/api/users/u/dodgefuski")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "dodgefuski"


@pytest.mark.asyncio
async def test_get_user_by_id(client: AsyncClient):
    # Create user
    create_resp = await client.post(
        "/api/users",
        json={
            "username": "virtualriot",
            "name": "Virtual Riot",
            "password": "securepassword123",
        },
    )
    user_id = create_resp.json()["id"]

    # Get user by user id
    response = await client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["username"] == "virtualriot"


@pytest.mark.asyncio
async def test_update_user(client: AsyncClient):
    # Create user
    create_resp = await client.post(
        "/api/users",
        json={
            "username": "codepandorum",
            "name": "INHUMAN",
            "password": "securepassword123",
        },
    )
    user_id = create_resp.json()["id"]

    # Update name
    response = await client.patch(
        f"/api/users/{user_id}",
        json={"name": "Code:Pandorum"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Code:Pandorum"
    assert response.json()["username"] == "codepandorum"


@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient):
    # Create user
    create_resp = await client.post(
        "/api/users",
        json={
            "username": "xilent",
            "name": "Xilent",
            "password": "securepassword123",
        },
    )
    user_id = create_resp.json()["id"]

    # Delete
    response = await client.delete(f"/api/users/{user_id}")
    assert response.status_code == 204

    # Verify it's gone
    get_resp = await client.get(f"/api/users/{user_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_create_user_invalid_data(client: AsyncClient):
    # Username too short (min 4)
    response = await client.post(
        "/api/users",
        json={"username": "jd", "name": "Jane Doe", "password": "short"},
    )
    assert response.status_code == 422  # Pydantic validation error
