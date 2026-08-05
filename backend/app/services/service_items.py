from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from core.models import ServiceItem
from core.models.mileage_log import MileageLog
from core.models.reminder import Reminder
from core.schemas import (
    ServiceItemCreate,
    ServiceItemMarkServiced,
    ServiceItemRead,
    ServiceItemStatus,
    ServiceItemSummary,
    ServiceItemUpdate,
)
from repositories import (
    CarRepository,
    MileageLogRepository,
    ReminderRepository,
    ServiceItemRepository,
)
from rules.mileage import validate_new_odometer

from .exceptions import CarNotFoundError, ServiceItemNotFoundError


class ServiceItemService:
    def __init__(
        self,
        session: AsyncSession,
        service_item_repository: ServiceItemRepository,
        car_repository: CarRepository,
        mileage_log_repository: MileageLogRepository,
        reminder_repository: ReminderRepository,
    ) -> None:
        self.session = session
        self.service_item_repository = service_item_repository
        self.car_repository = car_repository
        self.mileage_log_repository = mileage_log_repository
        self.reminder_repository = reminder_repository

    async def _get_item_with_owner_check(
        self,
        service_item_id: UUID,
        user_id: UUID,
    ) -> ServiceItem:
        service_item = await self.service_item_repository.get_by_id(service_item_id)
        if service_item is None or service_item.car.user_id != user_id:
            raise ServiceItemNotFoundError(service_item_id)
        return service_item

    async def add_service_item(
        self,
        create_schema: ServiceItemCreate,
        user_id: UUID,
    ) -> ServiceItemRead:
        _car = await self.car_repository.get_by_id(create_schema.car_id)
        if _car is None or _car.user_id != user_id:
            raise CarNotFoundError(create_schema.car_id)

        service_item = ServiceItem(
            car_id=create_schema.car_id,
            name=create_schema.name,
            last_service_at=create_schema.last_service_at,
            last_service_odometer_km=create_schema.last_service_odometer_km,
        )

        await self.service_item_repository.add(service_item)
        await self.session.commit()
        await self.session.refresh(service_item)

        return ServiceItemRead.model_validate(service_item)

    async def get_service_item(
        self,
        service_item_id: UUID,
        user_id: UUID,
    ) -> ServiceItemRead:
        service_item = await self._get_item_with_owner_check(service_item_id, user_id)
        return ServiceItemRead.model_validate(service_item)

    async def list_by_car(
        self,
        car_id: UUID,
        user_id: UUID,
    ) -> list[ServiceItemSummary]:
        car = await self.car_repository.get_by_id(car_id)
        if car is None or car.user_id != user_id:
            raise CarNotFoundError(car_id)

        service_items = await self.service_item_repository.list_by_car_id(car_id)

        if not service_items:
            return []

        latest_mileage = await self.mileage_log_repository.get_latest_for_car(car_id)
        current_odometer = (
            latest_mileage.odometer_km if latest_mileage else car.initial_odometer_km
        )

        item_ids = [item.id for item in service_items]
        reminders = await self.reminder_repository.list_active_by_service_item_ids(
            item_ids
        )

        reminders_map: dict[UUID, list[Reminder]] = {}
        for reminder in reminders:
            reminders_map.setdefault(reminder.service_item_id, []).append(reminder)

        now = datetime.now(UTC)
        results = []
        for item in service_items:
            item_reminders = reminders_map.get(item.id, [])

            status = ServiceItemStatus.OK
            km_until_due: int | None = None
            days_until_due: int | None = None

            if item_reminders:
                computed_reminders = []
                for reminder in item_reminders:
                    if reminder.interval_km:
                        due_at_km = item.last_service_odometer_km + reminder.interval_km
                        notify_at_km = due_at_km - (reminder.notify_before_km or 0)
                        km_left = due_at_km - current_odometer
                        _status = ServiceItemStatus.OK
                        if km_left <= 0:
                            _status = ServiceItemStatus.DUE
                        elif current_odometer >= notify_at_km:
                            _status = ServiceItemStatus.SOON
                        computed_reminders.append((_status, km_left, None))
                    if reminder.interval_days:
                        last_service_at = item.last_service_at
                        if last_service_at.tzinfo is None:
                            last_service_at = last_service_at.replace(tzinfo=UTC)

                        due_date = last_service_at + timedelta(
                            days=reminder.interval_days
                        )
                        notify_before = reminder.notify_before_days or 0
                        notify_date = due_date - timedelta(days=notify_before)
                        days_left = (due_date - now).days
                        _status = ServiceItemStatus.OK
                        if days_left <= 0:
                            _status = ServiceItemStatus.DUE
                        elif now >= notify_date:
                            _status = ServiceItemStatus.SOON
                        computed_reminders.append((_status, None, days_left))

                if any(rem[0] == ServiceItemStatus.DUE for rem in computed_reminders):
                    status = ServiceItemStatus.DUE
                    due_reminder = next(
                        r for r in computed_reminders if r[0] == ServiceItemStatus.DUE
                    )
                    km_until_due = due_reminder[1]
                    days_until_due = due_reminder[2]
                elif any(
                    rem[0] == ServiceItemStatus.SOON for rem in computed_reminders
                ):
                    status = ServiceItemStatus.SOON
                    soon_reminder = next(
                        r for r in computed_reminders if r[0] == ServiceItemStatus.SOON
                    )
                    km_until_due = soon_reminder[1]
                    days_until_due = soon_reminder[2]
                else:
                    valid = [
                        r
                        for r in computed_reminders
                        if r[1] is not None or r[2] is not None
                    ]
                    if valid:
                        km_until_due = min(
                            (r[1] for r in valid if r[1] is not None), default=None
                        )
                        days_until_due = min(
                            (r[2] for r in valid if r[2] is not None), default=None
                        )

            results.append(
                ServiceItemSummary(
                    id=item.id,
                    car_id=car.id,
                    name=item.name,
                    last_service_at=item.last_service_at,
                    last_service_odometer_km=item.last_service_odometer_km,
                    status=status,
                    km_until_due=km_until_due,
                    days_until_due=days_until_due,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                )
            )
        return results

    async def update_service_item(
        self,
        service_item_id: UUID,
        update_schema: ServiceItemUpdate,
        user_id: UUID,
    ) -> ServiceItemRead:
        service_item = await self._get_item_with_owner_check(service_item_id, user_id)

        update_data = update_schema.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(service_item, field, value)

        await self.session.commit()
        await self.session.refresh(service_item)

        return ServiceItemRead.model_validate(service_item)

    async def mark_serviced(
        self,
        service_item_id: UUID,
        mark_schema: ServiceItemMarkServiced,
        user_id: UUID,
    ) -> ServiceItemRead:
        service_item = await self._get_item_with_owner_check(service_item_id, user_id)

        car = await self.car_repository.get_by_id(service_item.car_id)
        if car is None:
            raise CarNotFoundError(service_item.car_id)

        latest_mileage = await self.mileage_log_repository.get_latest_for_car(
            service_item.car_id
        )
        current_odometer = (
            latest_mileage.odometer_km if latest_mileage else car.initial_odometer_km
        )

        validate_new_odometer(
            current_odometer_km=current_odometer,
            new_odometer_km=mark_schema.odometer_km,
        )

        if mark_schema.odometer_km > current_odometer:
            mileage_log = MileageLog(
                car_id=car.id,
                odometer_km=mark_schema.odometer_km,
            )
            await self.mileage_log_repository.add(mileage_log)

        service_item.last_service_at = mark_schema.serviced_at
        service_item.last_service_odometer_km = mark_schema.odometer_km

        await self.session.commit()
        await self.session.refresh(service_item)

        return ServiceItemRead.model_validate(service_item)

    async def delete_service_item(
        self,
        service_item_id: UUID,
        user_id: UUID,
    ) -> None:
        service_item = await self._get_item_with_owner_check(service_item_id, user_id)

        await self.service_item_repository.delete(service_item)
        await self.session.commit()
