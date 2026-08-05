import pytest
from httpx import AsyncClient

from core.config import settings


@pytest.mark.asyncio
async def test_telegram_disabled_status(client: AsyncClient):
    # Temporarily disable bot by setting token to None
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
