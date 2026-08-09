from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from core.models import UserSettings
from core.schemas.user_settings import UserSettingsRead, UserSettingsUpdate
from repositories import UserSettingsRepository
from services.exceptions import UserSettingsNotFoundError


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

        return UserSettingsRead.model_validate(settings)
