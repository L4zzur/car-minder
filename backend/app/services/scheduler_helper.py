import logging
from datetime import UTC, datetime, time, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from core.models.car import Car
from core.models.reminder import Reminder
from core.models.service_item import ServiceItem
from core.models.user_settings import UserSettings
from core.scheduler import scheduler

logger = logging.getLogger(__name__)


def get_user_timezone(user_settings: UserSettings | None) -> ZoneInfo:
    """Safely return user's ZoneInfo or default to UTC if invalid."""
    if user_settings and user_settings.timezone:
        try:
            return ZoneInfo(user_settings.timezone)
        except ZoneInfoNotFoundError:
            pass
    return ZoneInfo("UTC")


def calculate_reminder_target_datetime(
    last_service_at: datetime,
    interval_days: int,
    notify_before_days: int | None,
    preferred_time: time,
    tz: ZoneInfo,
) -> datetime:
    """Calculate exact UTC target datetime for a time-based reminder."""
    notify_days_offset = interval_days - (notify_before_days or 0)
    target_date = last_service_at.date() + timedelta(days=notify_days_offset)
    local_target = datetime.combine(target_date, preferred_time, tzinfo=tz)
    return local_target.astimezone(UTC)


def calculate_mileage_prompt_target_datetime(
    last_recorded_at: datetime,
    prompt_interval_days: int,
    preferred_time: time,
    tz: ZoneInfo,
) -> datetime:
    """Calculate exact UTC target datetime for an odometer prompt."""
    target_date = last_recorded_at.date() + timedelta(days=prompt_interval_days)
    local_target = datetime.combine(target_date, preferred_time, tzinfo=tz)
    return local_target.astimezone(UTC)


def sync_reminder_job(
    reminder: Reminder,
    service_item: ServiceItem,
    user_settings: UserSettings | None,
) -> None:
    """Register or update a reminder job in APScheduler if interval_days is set."""
    if not scheduler.running:
        return

    from tasks.jobs import send_service_reminder_job

    job_id = f"reminder_{reminder.id}"

    # Remove existing job if inactive or no interval_days
    if not reminder.is_active or not reminder.interval_days:
        try:
            scheduler.remove_job(job_id)
            logger.info(f"Removed job {job_id} from scheduler.")
        except Exception:
            pass
        return

    preferred_time = (
        user_settings.service_reminder_time if user_settings else time(12, 0)
    )
    tz = get_user_timezone(user_settings)

    run_date = calculate_reminder_target_datetime(
        last_service_at=service_item.last_service_at,
        interval_days=reminder.interval_days,
        notify_before_days=reminder.notify_before_days,
        preferred_time=preferred_time,
        tz=tz,
    )
    now_utc = datetime.now(UTC)
    reason = "Calculated due date is in the future."
    if run_date < now_utc:
        is_recently_notified = False
        if reminder.last_notified_at:
            last_notified = reminder.last_notified_at
            if last_notified.tzinfo is None:
                last_notified = last_notified.replace(tzinfo=UTC)
            if (now_utc - last_notified).total_seconds() < 12 * 3600:
                is_recently_notified = True

        if is_recently_notified:
            target_date = now_utc.date() + timedelta(days=1)
            local_target = datetime.combine(target_date, preferred_time, tzinfo=tz)
            run_date = local_target.astimezone(UTC)
            if run_date < now_utc:
                run_date = now_utc + timedelta(days=1)
            reason = "Already notified today; scheduled next check for tomorrow."
        else:
            run_date = now_utc + timedelta(seconds=2)
            reason = "Target time has passed; scheduled for immediate execution."

    scheduler.add_job(
        send_service_reminder_job,
        trigger="date",
        run_date=run_date,
        id=job_id,
        args=[reminder.id],
        replace_existing=True,
    )
    logger.info(
        f"[SCHEDULER] Scheduled job '{job_id}' for {run_date} UTC. Reason: {reason}"
    )


def remove_reminder_job(reminder_id: UUID) -> None:
    """Remove a reminder job from APScheduler."""
    if not scheduler.running:
        return
    job_id = f"reminder_{reminder_id}"
    try:
        scheduler.remove_job(job_id)
        logger.info(f"Removed job {job_id} from scheduler.")
    except Exception:
        pass


def remove_mileage_prompt_job(car_id: UUID) -> None:
    """Remove an odometer prompt job from APScheduler."""
    if not scheduler.running:
        return
    job_id = f"mileage_prompt_{car_id}"
    try:
        scheduler.remove_job(job_id)
        logger.info(f"Removed job {job_id} from scheduler.")
    except Exception:
        pass


def sync_mileage_prompt_job(
    car: Car,
    last_recorded_at: datetime,
    user_settings: UserSettings | None,
    already_prompted_today: bool = False,
) -> None:
    """Register or update an odometer prompt job in APScheduler."""
    if not scheduler.running:
        return

    from tasks.jobs import send_mileage_prompt_job

    job_id = f"mileage_prompt_{car.id}"

    interval_days = (
        user_settings.mileage_prompt_interval_days
        if user_settings and user_settings.mileage_prompt_interval_days is not None
        else 14
    )
    preferred_time = (
        user_settings.mileage_reminder_time if user_settings else time(19, 0)
    )
    tz = get_user_timezone(user_settings)

    run_date = calculate_mileage_prompt_target_datetime(
        last_recorded_at=last_recorded_at,
        prompt_interval_days=interval_days,
        preferred_time=preferred_time,
        tz=tz,
    )
    now_utc = datetime.now(UTC)
    reason = "Calculated prompt date is in the future."
    if run_date <= now_utc:
        if already_prompted_today:
            local_now = now_utc.astimezone(tz)
            tomorrow_date = local_now.date() + timedelta(days=1)
            local_target = datetime.combine(tomorrow_date, preferred_time, tzinfo=tz)
            run_date = local_target.astimezone(UTC)
            reason = "Already prompted; scheduled next check for tomorrow."
        else:
            run_date = now_utc + timedelta(seconds=2)
            reason = "Odometer prompt interval has passed; scheduled for immediate execution."

    scheduler.add_job(
        send_mileage_prompt_job,
        trigger="date",
        run_date=run_date,
        id=job_id,
        args=[car.id],
        replace_existing=True,
    )
    logger.info(
        f"[SCHEDULER] Scheduled mileage prompt job '{job_id}' for {run_date} UTC. Reason: {reason}"
    )
