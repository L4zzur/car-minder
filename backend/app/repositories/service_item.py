from uuid import UUID

from sqlalchemy import select
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
        return await self.session.get(ServiceItem, service_item_id)

    async def list_by_car_id(self, car_id: UUID) -> list[ServiceItem]:
        stmt = select(ServiceItem).where(
            ServiceItem.car_id == car_id,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
