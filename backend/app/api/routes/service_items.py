from uuid import UUID

from fastapi import APIRouter, Depends

from api.deps import get_service_item_service
from core.schemas import (
    ServiceItemCreate,
    ServiceItemMarkServiced,
    ServiceItemRead,
    ServiceItemUpdate,
)
from services import ServiceItemService
from services.exceptions import ServiceItemNotFoundError

router = APIRouter(prefix="/service-items", tags=["service-items"])


@router.post("", response_model=ServiceItemRead, status_code=201)
async def add_service_item(
    create_schema: ServiceItemCreate,
    service: ServiceItemService = Depends(get_service_item_service),
) -> ServiceItemRead:
    return await service.add_service_item(create_schema)


@router.get("/car/{car_id}", response_model=list[ServiceItemRead], status_code=200)
async def list_by_car(
    car_id: UUID,
    service: ServiceItemService = Depends(get_service_item_service),
) -> list[ServiceItemRead]:
    return await service.list_by_car(car_id)


@router.get("/{service_item_id}", response_model=ServiceItemRead, status_code=200)
async def get_service_item(
    service_item_id: UUID,
    service: ServiceItemService = Depends(get_service_item_service),
) -> ServiceItemRead:
    service_item = await service.get_service_item(service_item_id)
    if service_item is None:
        raise ServiceItemNotFoundError(service_item_id)
    return service_item


@router.patch("/{service_item_id}", response_model=ServiceItemRead, status_code=200)
async def update_service_item(
    service_item_id: UUID,
    update_schema: ServiceItemUpdate,
    service: ServiceItemService = Depends(get_service_item_service),
) -> ServiceItemRead:
    return await service.update_service_item(service_item_id, update_schema)


@router.post(
    "/{service_item_id}/mark-serviced", response_model=ServiceItemRead, status_code=200
)
async def mark_serviced(
    service_item_id: UUID,
    mark_schema: ServiceItemMarkServiced,
    service: ServiceItemService = Depends(get_service_item_service),
) -> ServiceItemRead:
    return await service.mark_serviced(service_item_id, mark_schema)


@router.delete("/{service_item_id}", status_code=204)
async def delete_service_item(
    service_item_id: UUID,
    service: ServiceItemService = Depends(get_service_item_service),
) -> None:
    await service.delete_service_item(service_item_id)
