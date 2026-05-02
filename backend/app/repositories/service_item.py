from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import ServiceItem


class ServiceItemRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, service_item: ServiceItem) -> None:
        self.session.add(service_item)
        await self.session.flush()

    async def delete(self, service_item: ServiceItem) -> None:
        await self.session.delete(service_item)
        await self.session.flush()

    async def get_by_id(self, service_item_id: UUID) -> ServiceItem | None:
        stmt = (
            select(ServiceItem)
            .where(ServiceItem.id == service_item_id)
            .options(selectinload(ServiceItem.car))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_by_car_id(self, car_id: UUID) -> list[ServiceItem]:
        stmt = select(ServiceItem).where(
            ServiceItem.car_id == car_id,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
