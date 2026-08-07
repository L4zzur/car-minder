import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_change_password(
    auth_client: AsyncClient,
    test_user: dict,
    user_password: str,
) -> None:
    change_req = {
        "current_password": user_password,
        "new_password": "newsecretpassword123",
    }
    response = await auth_client.post("/api/auth/change-password", json=change_req)
    assert response.status_code == 204

    # Verify old password fails login
    login_data = {
        "username": test_user["username"],
        "password": user_password,
    }
    fail_res = await auth_client.post("/api/auth/login", data=login_data)
    assert fail_res.status_code == 401

    # Verify new password succeeds login
    login_data_new = {
        "username": test_user["username"],
        "password": "newsecretpassword123",
    }
    succ_res = await auth_client.post("/api/auth/login", data=login_data_new)
    assert succ_res.status_code == 200


@pytest.mark.asyncio
async def test_change_password_invalid_current(
    auth_client: AsyncClient,
) -> None:
    change_req = {
        "current_password": "wrong_current_password",
        "new_password": "newsecretpassword123",
    }
    response = await auth_client.post("/api/auth/change-password", json=change_req)
    assert response.status_code == 422
    assert response.json()["code"] == "invalid_current_password"
