from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import UserSettings


class UserSettingsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, settings: UserSettings) -> None:
        self.session.add(settings)
        await self.session.flush()

    async def get_by_user_id(self, user_id: UUID) -> UserSettings | None:
        stmt = select(UserSettings).where(UserSettings.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()
