import logging
from datetime import UTC, datetime
from uuid import UUID

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot import bot, i18n_core
from core.db_helper import db_helper
from repositories.car import CarRepository
from repositories.mileage_log import MileageLogRepository
from repositories.reminder import ReminderRepository

logger = logging.getLogger(__name__)


async def send_service_reminder_job(reminder_id: UUID | str) -> None:
    """Executes a scheduled service reminder task and notifies the user via Telegram."""
    if not bot:
        logger.warning("Telegram bot is not initialized; skipping reminder job.")
        return

    if isinstance(reminder_id, str):
        reminder_id = UUID(reminder_id)

    async with db_helper.session_factory() as session:
        reminder_repo = ReminderRepository(session)
        reminder = await reminder_repo.get_with_relations(reminder_id)

        if not reminder or not reminder.is_active:
            logger.info(
                f"Reminder {reminder_id} is inactive or deleted; skipping notification."
            )
            return

        service_item = reminder.service_item
        if not service_item:
            return

        car = service_item.car
        if not car or not car.user:
            return

        user = car.user
        user_settings = user.settings

        if (
            not user.telegram_id
            or not user_settings
            or not user_settings.notify_via_telegram
        ):
            logger.info(
                f"User {user.id} has disabled Telegram notifications or has no telegram_id."
            )
            return

        now_utc = datetime.now(UTC)

        # Anti-spam deduplication: skip if notified within the last 12 hours
        if reminder.last_notified_at:
            last_notified = reminder.last_notified_at
            if last_notified.tzinfo is None:
                last_notified = last_notified.replace(tzinfo=UTC)
            if (now_utc - last_notified).total_seconds() < 12 * 3600:
                logger.info(
                    f"Reminder {reminder_id} was already sent recently ({reminder.last_notified_at}); skipping."
                )
                return

        mileage_repo = MileageLogRepository(session)
        latest_log = await mileage_repo.get_latest_for_car(car.id)
        current_odometer_km = (
            latest_log.odometer_km if latest_log else car.initial_odometer_km
        )

        locale = user_settings.language or "ru"

        title = i18n_core.get(
            "service_reminder_title",
            locale=locale,
            car_brand=car.brand,
            car_model=car.model,
        )
        item_line = i18n_core.get(
            "service_reminder_item",
            locale=locale,
            item_name=service_item.name,
        )

        reason_line = ""
        if reminder.interval_days:
            days_passed = (now_utc.date() - service_item.last_service_at.date()).days
            days_left = reminder.interval_days - days_passed
            if days_left <= 0:
                reason_line = i18n_core.get("service_reminder_overdue", locale=locale)
            else:
                reason_line = i18n_core.get(
                    "service_reminder_reason_days",
                    locale=locale,
                    days_left=days_left,
                )
        elif reminder.interval_km:
            km_passed = current_odometer_km - service_item.last_service_odometer_km
            km_left = reminder.interval_km - km_passed
            if km_left <= 0:
                reason_line = i18n_core.get("service_reminder_overdue", locale=locale)
            else:
                reason_line = i18n_core.get(
                    "service_reminder_reason_km",
                    locale=locale,
                    km_left=km_left,
                )

        text_lines = [title, "", item_line]
        if reason_line:
            text_lines.append(reason_line)

        if reminder.note:
            text_lines.append(f"📝 <i>{reminder.note}</i>")

        message_text = "\n".join(text_lines)

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=i18n_core.get("mark_service_done_button", locale=locale),
                        callback_data=f"mark_serviced:{service_item.id}",
                    )
                ]
            ]
        )

        try:
            await bot.send_message(
                chat_id=user.telegram_id,
                text=message_text,
                reply_markup=keyboard,
            )
            reminder.last_notified_at = now_utc
            await session.commit()
            logger.info(
                f"Successfully sent service reminder {reminder_id} to user {user.id} (telegram_id={user.telegram_id})."
            )
        except Exception as e:
            logger.error(
                f"Failed to send Telegram reminder {reminder_id} to chat {user.telegram_id}: {e}"
            )


async def send_mileage_prompt_job(car_id: UUID | str) -> None:
    """Executes a scheduled odometer prompt task and asks the user to update mileage."""
    if not bot:
        logger.warning("Telegram bot is not initialized; skipping mileage prompt job.")
        return

    if isinstance(car_id, str):
        car_id = UUID(car_id)

    async with db_helper.session_factory() as session:
        car_repo = CarRepository(session)
        car = await car_repo.get_with_user(car_id)

        if not car or not car.user:
            return

        user = car.user
        user_settings = user.settings

        if (
            not user.telegram_id
            or not user_settings
            or not user_settings.notify_via_telegram
        ):
            logger.info(
                f"User {user.id} has disabled Telegram notifications or has no telegram_id."
            )
            return

        prompt_interval = user_settings.mileage_prompt_interval_days or 14

        mileage_repo = MileageLogRepository(session)
        latest_log = await mileage_repo.get_latest_for_car(car_id)

        now_utc = datetime.now(UTC)
        if latest_log:
            last_recorded = latest_log.created_at
            if last_recorded.tzinfo is None:
                last_recorded = last_recorded.replace(tzinfo=UTC)
            days_since_last = (now_utc - last_recorded).days
            if days_since_last < prompt_interval:
                logger.info(
                    f"Car {car_id} mileage was updated {days_since_last} days ago; skipping prompt."
                )
                return
            current_km = latest_log.odometer_km
        else:
            days_since_last = prompt_interval
            current_km = car.initial_odometer_km

        locale = user_settings.language or "ru"

        title = i18n_core.get(
            "mileage_prompt_title",
            locale=locale,
            car_brand=car.brand,
            car_model=car.model,
        )
        body = i18n_core.get(
            "mileage_prompt_body",
            locale=locale,
            days=days_since_last,
            current_km=current_km,
        )

        message_text = f"{title}\n\n{body}"

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=i18n_core.get("update_mileage_button", locale=locale),
                        callback_data=f"prompt_mileage:{car.id}",
                    )
                ]
            ]
        )

        try:
            await bot.send_message(
                chat_id=user.telegram_id,
                text=message_text,
                reply_markup=keyboard,
            )
            logger.info(
                f"Successfully sent mileage prompt for car {car_id} to user {user.id}."
            )
        except Exception as e:
            logger.error(
                f"Failed to send mileage prompt for car {car_id} to chat {user.telegram_id}: {e}"
            )
