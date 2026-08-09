from datetime import UTC, datetime, time
from zoneinfo import ZoneInfo

from core.models.user_settings import UserSettings
from services.scheduler_helper import (
    calculate_mileage_prompt_target_datetime,
    calculate_reminder_target_datetime,
    get_user_timezone,
)


def test_get_user_timezone_default():
    tz = get_user_timezone(None)
    assert tz == ZoneInfo("UTC")


def test_get_user_timezone_valid():
    settings = UserSettings(timezone="Europe/Moscow")
    tz = get_user_timezone(settings)
    assert tz == ZoneInfo("Europe/Moscow")


def test_get_user_timezone_invalid():
    settings = UserSettings(timezone="Invalid/Timezone_Name")
    tz = get_user_timezone(settings)
    assert tz == ZoneInfo("UTC")


def test_calculate_reminder_target_datetime():
    last_service_at = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    interval_days = 30
    notify_before_days = 5
    preferred_time = time(18, 20)
    tz = ZoneInfo("Europe/Moscow")

    target_dt = calculate_reminder_target_datetime(
        last_service_at=last_service_at,
        interval_days=interval_days,
        notify_before_days=notify_before_days,
        preferred_time=preferred_time,
        tz=tz,
    )
    # Expected target date: Jan 1 + (30 - 5) = Jan 26. Time: 18:20 MSK (UTC+3) -> 15:20 UTC
    assert target_dt.hour == 15
    assert target_dt.minute == 20
    assert target_dt.day == 26
    assert target_dt.month == 1


def test_calculate_mileage_prompt_target_datetime():
    last_recorded_at = datetime(2026, 5, 10, 10, 0, tzinfo=UTC)
    prompt_interval_days = 14
    preferred_time = time(19, 0)
    tz = ZoneInfo("Europe/Moscow")

    target_dt = calculate_mileage_prompt_target_datetime(
        last_recorded_at=last_recorded_at,
        prompt_interval_days=prompt_interval_days,
        preferred_time=preferred_time,
        tz=tz,
    )
    # Expected target date: May 10 + 14 = May 24. Time: 19:00 MSK (UTC+3) -> 16:00 UTC
    assert target_dt.hour == 16
    assert target_dt.minute == 0
    assert target_dt.day == 24
    assert target_dt.month == 5
