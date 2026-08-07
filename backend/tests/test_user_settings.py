import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_user_settings_default(
    auth_client: AsyncClient,
) -> None:
    response = await auth_client.get("/api/users/me/settings")
    assert response.status_code == 200
    data = response.json()
    assert data["service_reminder_time"] == "12:00:00"
    assert data["mileage_reminder_time"] == "19:00:00"
    assert data["mileage_prompt_interval_days"] == 14
    assert data["timezone"] == "Europe/Moscow"
    assert data["notify_via_telegram"] is True
    assert data["notify_via_email"] is False
    assert data["language"] == "ru"


@pytest.mark.asyncio
async def test_update_user_settings(
    auth_client: AsyncClient,
) -> None:
    update_data = {
        "service_reminder_time": "10:30:00",
        "mileage_reminder_time": "20:15:00",
        "mileage_prompt_interval_days": 7,
        "timezone": "UTC",
        "notify_via_telegram": False,
        "notify_via_email": True,
        "language": "en",
    }
    response = await auth_client.patch("/api/users/me/settings", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["service_reminder_time"] == "10:30:00"
    assert data["mileage_reminder_time"] == "20:15:00"
    assert data["mileage_prompt_interval_days"] == 7
    assert data["timezone"] == "UTC"
    assert data["notify_via_telegram"] is False
    assert data["notify_via_email"] is True
    assert data["language"] == "en"


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
