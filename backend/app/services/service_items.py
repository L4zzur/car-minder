from uuid import UUID

from core.models import ServiceItem
from core.schemas.service_item import (
    ServiceItemCreate,
    ServiceItemRead,
    ServiceItemUpdate,
)
from repositories import CarRepository, ServiceItemRepository
from sqlalchemy.ext.asyncio import AsyncSession

from .exceptions import CarNotFoundError, ServiceItemNotFoundError


class ServiceItemService:
    def __init__(
        self,
        session: AsyncSession,
        service_item_repository: ServiceItemRepository,
        car_repository: CarRepository,
    ) -> None:
        self.session = session
        self.service_item_repository = service_item_repository
        self.car_repository = car_repository

    async def add_service_item(
        self,
        create_schema: ServiceItemCreate,
    ) -> ServiceItemRead:
        _car = await self.car_repository.get_by_id(create_schema.car_id)
        if _car is None:
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
    ) -> ServiceItemRead | None:
        service_item = await self.service_item_repository.get_by_id(service_item_id)
        return ServiceItemRead.model_validate(service_item) if service_item else None

    async def list_by_car(
        self,
        car_id: UUID,
    ) -> list[ServiceItemRead]:
        _car = await self.car_repository.get_by_id(car_id)
        if _car is None:
            raise CarNotFoundError(car_id)

        service_items = await self.service_item_repository.list_by_car_id(car_id)
        return [
            ServiceItemRead.model_validate(service_item)
            for service_item in service_items
        ]

    async def update_service_item(
        self,
        service_item_id: UUID,
        update_schema: ServiceItemUpdate,
    ) -> ServiceItemRead:
        service_item = await self.service_item_repository.get_by_id(service_item_id)
        if service_item is None:
            raise ServiceItemNotFoundError(service_item_id)

        update_data = update_schema.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(service_item, field, value)

        await self.session.commit()
        await self.session.refresh(service_item)

        return ServiceItemRead.model_validate(service_item)

    async def delete_service_item(
        self,
        service_item_id: UUID,
    ) -> None:
        service_item = await self.service_item_repository.get_by_id(service_item_id)
        if service_item is None:
            raise ServiceItemNotFoundError(service_item_id)

        await self.service_item_repository.delete(service_item)
        await self.session.commit()
