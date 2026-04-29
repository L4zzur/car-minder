from uuid import UUID

from core.models import Reminder
from core.schemas import (
    ReminderCreate,
    ReminderRead,
    ReminderUpdate,
)
from core.validators import ReminderIntervalData, validate_reminder_intervals
from repositories import ReminderRepository, ServiceItemRepository
from sqlalchemy.ext.asyncio import AsyncSession

from .exceptions import (
    ReminderIntervalError,
    ReminderNotFoundError,
    ServiceItemNotFoundError,
)


class ReminderService:
    def __init__(
        self,
        session: AsyncSession,
        reminder_repository: ReminderRepository,
        service_item_repository: ServiceItemRepository,
    ) -> None:
        self.session = session
        self.reminder_repository = reminder_repository
        self.service_item_repository = service_item_repository

    async def add_reminder(
        self,
        create_schema: ReminderCreate,
    ) -> ReminderRead:
        _service_item = await self.service_item_repository.get_by_id(
            create_schema.service_item_id
        )
        if _service_item is None:
            raise ServiceItemNotFoundError(create_schema.service_item_id)

        reminder = Reminder(
            service_item_id=create_schema.service_item_id,
            is_active=create_schema.is_active,
            interval_km=create_schema.interval_km,
            interval_days=create_schema.interval_days,
            notify_before_km=create_schema.notify_before_km,
            notify_before_days=create_schema.notify_before_days,
            note=create_schema.note,
        )

        await self.reminder_repository.add(reminder)
        await self.session.commit()
        await self.session.refresh(reminder)

        return ReminderRead.model_validate(reminder)

    async def get_reminder(
        self,
        reminder_id: UUID,
    ) -> ReminderRead | None:
        reminder = await self.reminder_repository.get_by_id(reminder_id)
        return ReminderRead.model_validate(reminder) if reminder else None

    async def list_by_service_item(
        self,
        service_item_id: UUID,
    ) -> list[ReminderRead]:
        _service_item = await self.service_item_repository.get_by_id(service_item_id)
        if _service_item is None:
            raise ServiceItemNotFoundError(service_item_id)

        reminders = await self.reminder_repository.list_by_service_item_id(
            service_item_id
        )
        return [ReminderRead.model_validate(reminder) for reminder in reminders]

    async def list_active_by_service_item(
        self,
        service_item_id: UUID,
    ) -> list[ReminderRead]:
        _service_item = await self.service_item_repository.get_by_id(service_item_id)
        if _service_item is None:
            raise ServiceItemNotFoundError(service_item_id)

        reminders = await self.reminder_repository.list_active_by_service_item_id(
            service_item_id
        )
        return [ReminderRead.model_validate(reminder) for reminder in reminders]

    async def update_reminder(
        self,
        reminder_id: UUID,
        update_schema: ReminderUpdate,
    ) -> ReminderRead:
        reminder = await self.reminder_repository.get_by_id(reminder_id)
        if reminder is None:
            raise ReminderNotFoundError(reminder_id)

        update_data = update_schema.model_dump(exclude_unset=True)
        try:
            validate_reminder_intervals(
                ReminderIntervalData(
                    interval_km=update_data.get("interval_km", reminder.interval_km),
                    interval_days=update_data.get(
                        "interval_days", reminder.interval_days
                    ),
                    notify_before_km=update_data.get(
                        "notify_before_km",
                        reminder.notify_before_km,
                    ),
                    notify_before_days=update_data.get(
                        "notify_before_days",
                        reminder.notify_before_days,
                    ),
                )
            )
        except ValueError as exc:
            raise ReminderIntervalError(
                interval_km=reminder.interval_km,
                interval_days=reminder.interval_days,
                notify_before_km=reminder.notify_before_km,
                notify_before_days=reminder.notify_before_days,
                reason=str(exc),
            ) from exc

        for field, value in update_data.items():
            setattr(reminder, field, value)

        await self.session.commit()
        await self.session.refresh(reminder)

        return ReminderRead.model_validate(reminder)

    async def delete_reminder(
        self,
        reminder_id: UUID,
    ) -> None:
        reminder = await self.reminder_repository.get_by_id(reminder_id)
        if reminder is None:
            raise ReminderNotFoundError(reminder_id)

        await self.reminder_repository.delete(reminder)
        await self.session.commit()
