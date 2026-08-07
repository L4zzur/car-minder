import hashlib
import hmac
import json
import time
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from core.config import settings


def create_telegram_init_data(bot_token: str, user_dict: dict) -> str:
    """Helper to generate a valid Telegram WebApp initData string with HMAC-SHA256 signature."""
    from urllib.parse import urlencode

    auth_date = int(time.time())
    data = {
        "auth_date": str(auth_date),
        "query_id": "AAH_TEST_QUERY_ID",
        "user": json.dumps(user_dict, separators=(",", ":")),
    }
    data_check_string = "\n".join(f"{k}={data[k]}" for k in sorted(data.keys()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    hash_value = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()
    data["hash"] = hash_value
    return urlencode(data)


@pytest.mark.asyncio
async def test_telegram_disabled_status(client: AsyncClient):
    """When bot token is None, endpoints return 503 disabled."""
    original_token = settings.bot.token
    settings.bot.token = None

    try:
        response = await client.get("/api/telegram/webhook")
        assert response.status_code == 200
        assert response.json() == {"status": "Telegram bot is disabled"}

        response = await client.post(
            "/api/telegram/webhook",
            headers={"X-Telegram-Bot-Api-Secret-Token": "invalid"},
        )
        assert response.status_code == 503
        assert response.json()["detail"] == "Telegram bot is disabled"
    finally:
        settings.bot.token = original_token


@pytest.mark.asyncio
async def test_webhook_invalid_secret_token_returns_403(client: AsyncClient):
    """POST /api/telegram/webhook with invalid secret token header returns 403 Forbidden."""
    resp = await client.post(
        "/api/telegram/webhook",
        json={"update_id": 123},
        headers={"X-Telegram-Bot-Api-Secret-Token": "wrong_secret_token"},
    )
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Invalid Secret Token"


@pytest.mark.asyncio
async def test_webhook_valid_secret_token_processes_update(client: AsyncClient):
    """POST /api/telegram/webhook with valid secret processes update and returns 200 OK."""
    secret = settings.bot.webhook_secret.get_secret_value()

    update_payload = {
        "update_id": 10001,
        "message": {
            "message_id": 1,
            "date": int(time.time()),
            "chat": {"id": 99999, "type": "private"},
            "from": {"id": 99999, "is_bot": False, "first_name": "Tester"},
            "text": "/start",
        },
    }

    with patch("bot.dp.feed_update", new_callable=AsyncMock) as mock_feed:
        resp = await client.post(
            "/api/telegram/webhook",
            json=update_payload,
            headers={"X-Telegram-Bot-Api-Secret-Token": secret},
        )
        assert resp.status_code == 200
        assert resp.json() == {"ok": True}
        mock_feed.assert_called_once()


@pytest.mark.asyncio
async def test_generate_link_token_and_unlink(
    auth_client: AsyncClient, test_user: dict
):
    """LoggedIn user can request link token, and unlinking when not linked returns 422."""
    # Generate link token
    resp = await auth_client.post("/api/telegram/link-token")
    assert resp.status_code == 200
    assert "token" in resp.json()

    # Unlink when no telegram is linked
    unlink_resp = await auth_client.delete("/api/telegram/link")
    assert unlink_resp.status_code == 422
    assert unlink_resp.json()["code"] == "telegram_not_linked"


@pytest.mark.asyncio
async def test_telegram_auth_miniapp_valid_init_data(
    client: AsyncClient, test_user: dict, session
):
    """MiniApp auth with valid HMAC signature authenticates user and sets cookies."""
    from uuid import UUID

    from repositories import UserRepository

    tg_id = 888777666
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(UUID(test_user["id"]))
    assert user is not None
    user.telegram_id = tg_id
    await session.commit()

    bot_token = settings.bot.token.get_secret_value()
    valid_init_data = create_telegram_init_data(
        bot_token, {"id": tg_id, "first_name": "TestUser"}
    )

    resp = await client.post(
        "/api/telegram/auth",
        json={"init_data_raw": valid_init_data},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()
    assert "access_token" in resp.cookies


@pytest.mark.asyncio
async def test_telegram_auth_miniapp_invalid_init_data_fails(client: AsyncClient):
    """MiniApp auth with invalid/tampered initData returns error."""
    resp = await client.post(
        "/api/telegram/auth",
        json={"init_data_raw": "query_id=123&user={}&hash=bad_hash"},
    )
    assert resp.status_code == 401
