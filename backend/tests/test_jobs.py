from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tasks.jobs import send_mileage_prompt_job, send_service_reminder_job


@pytest.mark.asyncio
async def test_send_service_reminder_job_inactive(
    session: AsyncSession, auth_client: AsyncClient, test_service_item: dict
):
    item_id = test_service_item["id"]
    create_resp = await auth_client.post(
        "/api/reminders",
        json={
            "service_item_id": item_id,
            "interval_km": 5000,
            "is_active": False,
        },
    )
    rem_id = create_resp.json()["id"]

    with patch("tasks.jobs.bot") as mock_bot:
        mock_bot.send_message = AsyncMock()
        await send_service_reminder_job(rem_id)
        mock_bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_send_service_reminder_job_nonexistent(session: AsyncSession):
    with patch("tasks.jobs.bot") as mock_bot:
        mock_bot.send_message = AsyncMock()
        await send_service_reminder_job(uuid4())
        mock_bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_send_mileage_prompt_job_nonexistent(session: AsyncSession):
    with patch("tasks.jobs.bot") as mock_bot:
        mock_bot.send_message = AsyncMock()
        await send_mileage_prompt_job(uuid4())
        mock_bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_send_service_reminder_job_active(
    session: AsyncSession,
    auth_client: AsyncClient,
    test_user: dict,
    test_service_item: dict,
):
    # Link telegram ID to user for testing
    from uuid import UUID

    from repositories.user import UserRepository

    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(UUID(test_user["id"]))
    assert user is not None
    user.telegram_id = 999888777
    await session.commit()

    item_id = test_service_item["id"]
    create_resp = await auth_client.post(
        "/api/reminders",
        json={
            "service_item_id": item_id,
            "interval_days": 10,
            "is_active": True,
        },
    )
    rem_id = create_resp.json()["id"]

    with patch("tasks.jobs.bot") as mock_bot:
        mock_bot.send_message = AsyncMock()
        await send_service_reminder_job(rem_id)
        mock_bot.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_send_mileage_prompt_job_force(
    session: AsyncSession,
    auth_client: AsyncClient,
    test_user: dict,
    test_car: dict,
):
    from uuid import UUID

    from repositories.user import UserRepository

    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(UUID(test_user["id"]))
    assert user is not None
    user.telegram_id = 999888772
    await session.commit()

    with patch("tasks.jobs.bot") as mock_bot:
        mock_bot.send_message = AsyncMock()
        await send_mileage_prompt_job(test_car["id"], force=True)
        mock_bot.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_update_settings_resyncs_jobs(
    auth_client: AsyncClient,
    test_service_item: dict,
):
    # Create reminder
    await auth_client.post(
        "/api/reminders",
        json={
            "service_item_id": test_service_item["id"],
            "interval_days": 10,
            "is_active": True,
        },
    )

    # Update settings
    resp = await auth_client.patch(
        "/api/users/me/settings",
        json={
            "service_reminder_time": "18:00:00",
            "timezone": "Europe/Moscow",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["service_reminder_time"] == "18:00:00"


@pytest.mark.asyncio
async def test_send_service_reminder_job_bot_error_handles_gracefully(
    session: AsyncSession,
    auth_client: AsyncClient,
    test_user: dict,
    test_service_item: dict,
):
    from uuid import UUID

    from repositories.user import UserRepository

    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(UUID(test_user["id"]))
    assert user is not None
    user.telegram_id = 999888776
    await session.commit()

    item_id = test_service_item["id"]
    create_resp = await auth_client.post(
        "/api/reminders",
        json={
            "service_item_id": item_id,
            "interval_days": 10,
            "is_active": True,
        },
    )
    rem_id = create_resp.json()["id"]

    with patch("tasks.jobs.bot") as mock_bot:
        mock_bot.send_message = AsyncMock(side_effect=Exception("Telegram bot blocked"))
        # Should not raise exception, logs error and reschedules for tomorrow
        await send_service_reminder_job(rem_id)
        mock_bot.send_message.assert_called_once()

