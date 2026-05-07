from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models import Reminder, ServiceItem


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
        stmt = (
            select(Reminder)
            .where(Reminder.id == reminder_id)
            .options(selectinload(Reminder.service_item).selectinload(ServiceItem.car))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

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

    async def list_active_by_service_item_ids(
        self, service_item_ids: list[UUID]
    ) -> list[Reminder]:
        """Fetch all active reminders for a list of service items."""
        if not service_item_ids:
            return []
        stmt = select(Reminder).where(
            Reminder.service_item_id.in_(service_item_ids),
            Reminder.is_active.is_(True),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
