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
async def test_update_user(auth_client: AsyncClient, test_user: dict):
    # Update name
    user_id = test_user["id"]
    response = await auth_client.patch(
        f"/api/users/{user_id}",
        json={"name": "Code:Pandorum"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Code:Pandorum"
    assert response.json()["username"] == test_user["username"]


@pytest.mark.asyncio
async def test_delete_user(
    auth_client: AsyncClient, client: AsyncClient, test_user: dict
):
    # Delete
    user_id = test_user["id"]
    response = await auth_client.delete(f"/api/users/{user_id}")
    assert response.status_code == 204

    # Verify it's gone
    get_resp = await client.get(f"/api/users/{user_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_update_user_unauthorized(client: AsyncClient, test_user: dict):
    response = await client.patch(
        f"/api/users/{test_user['id']}",
        json={"name": "Nope"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_user_unauthorized(client: AsyncClient, test_user: dict):
    response = await client.delete(f"/api/users/{test_user['id']}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_other_user_forbidden(
    client: AsyncClient,
    auth_client: AsyncClient,
):
    create_resp = await client.post(
        "/api/users",
        json={
            "username": "forbidden_target",
            "name": "Forbidden Target",
            "password": "securepassword123",
        },
    )
    user_id = create_resp.json()["id"]

    response = await auth_client.patch(
        f"/api/users/{user_id}",
        json={"name": "Nope"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_user_invalid_data(client: AsyncClient):
    # Username too short (min 4)
    response = await client.post(
        "/api/users",
        json={"username": "jd", "name": "Jane Doe", "password": "short"},
    )
    assert response.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
async def test_create_user_duplicate_email(client: AsyncClient):
    await client.post(
        "/api/users",
        json={
            "username": "emailuser1",
            "name": "Email User 1",
            "email": "duplicate@example.com",
            "password": "password123",
        },
    )
    response = await client.post(
        "/api/users",
        json={
            "username": "emailuser2",
            "name": "Email User 2",
            "email": "duplicate@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 409
    assert response.json()["code"] == "email_already_taken"


@pytest.mark.asyncio
async def test_update_user_email(auth_client: AsyncClient, test_user: dict):
    user_id = test_user["id"]
    response = await auth_client.patch(
        f"/api/users/{user_id}",
        json={"email": "my_new_email@example.com"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "my_new_email@example.com"


@pytest.mark.asyncio
async def test_update_user_duplicate_email(
    client: AsyncClient,
    auth_client: AsyncClient,
    test_user: dict,
):
    # Create another user with an email
    await client.post(
        "/api/users",
        json={
            "username": "other_user_email",
            "name": "Other User",
            "email": "taken_by_other@example.com",
            "password": "password123",
        },
    )

    # Try to update test_user email to taken_by_other@example.com
    user_id = test_user["id"]
    response = await auth_client.patch(
        f"/api/users/{user_id}",
        json={"email": "taken_by_other@example.com"},
    )
    assert response.status_code == 409
    assert response.json()["code"] == "email_already_taken"
