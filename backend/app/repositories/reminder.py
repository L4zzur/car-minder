from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Reminder


class ReminderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, reminder: Reminder) -> None:
        self.session.add(reminder)
        await self.session.flush()

    async def delete(self, reminder: Reminder) -> None:
        await self.session.delete(reminder)
        await self.session.flush()

    async def get_by_id(self, reminder_id: UUID) -> Reminder | None:
        return await self.session.get(Reminder, reminder_id)

    async def list_by_service_item_id(self, service_item_id: UUID) -> list[Reminder]:
        stmt = select(Reminder).where(
            Reminder.service_item_id == service_item_id,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_active_by_service_item_id(
        self, service_item_id: UUID
    ) -> list[Reminder]:
        stmt = select(Reminder).where(
            Reminder.service_item_id == service_item_id,
            Reminder.is_active.is_(True),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
