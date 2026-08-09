from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from core.models import UserSettings
from core.schemas.user_settings import UserSettingsRead, UserSettingsUpdate
from repositories import (
    CarRepository,
    MileageLogRepository,
    ReminderRepository,
    UserSettingsRepository,
)
from services.exceptions import UserSettingsNotFoundError
from services.scheduler_helper import (
    sync_mileage_prompt_job,
    sync_reminder_job,
)


class UserSettingsService:
    def __init__(
        self,
        session: AsyncSession,
        settings_repository: UserSettingsRepository,
    ) -> None:
        self.session = session
        self.settings_repository = settings_repository

    async def get_settings(self, user_id: UUID) -> UserSettingsRead:
        settings = await self.settings_repository.get_by_user_id(user_id)
        if not settings:
            raise UserSettingsNotFoundError(user_id)

        return UserSettingsRead.model_validate(settings)

    async def update_settings(
        self,
        user_id: UUID,
        update_schema: UserSettingsUpdate,
    ) -> UserSettingsRead:
        settings = await self.settings_repository.get_by_user_id(user_id)
        if not settings:
            settings = UserSettings(user_id=user_id)
            self.session.add(settings)

        update_data = update_schema.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(settings, field, value)

        await self.session.commit()
        await self.session.refresh(settings)

        # Re-sync all scheduled jobs for user's reminders and cars with new settings
        reminder_repo = ReminderRepository(self.session)
        car_repo = CarRepository(self.session)
        mileage_repo = MileageLogRepository(self.session)

        user_reminders = await reminder_repo.list_by_user_id(user_id)
        for reminder in user_reminders:
            if reminder.service_item:
                sync_reminder_job(reminder, reminder.service_item, settings)

        user_cars = await car_repo.list_by_user_id(user_id)
        for car in user_cars:
            latest_log = await mileage_repo.get_latest_for_car(car.id)
            last_recorded = latest_log.created_at if latest_log else car.created_at
            sync_mileage_prompt_job(car, last_recorded, settings)

        return UserSettingsRead.model_validate(settings)
