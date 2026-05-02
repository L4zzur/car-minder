from uuid import UUID

from fastapi import APIRouter, Depends

from api.deps import get_current_user, get_service_item_service
from core.models import User
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
    current_user: User = Depends(get_current_user),
    service: ServiceItemService = Depends(get_service_item_service),
) -> ServiceItemRead:
    return await service.add_service_item(create_schema, current_user.id)


@router.get("/car/{car_id}", response_model=list[ServiceItemRead], status_code=200)
async def list_by_car(
    car_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ServiceItemService = Depends(get_service_item_service),
) -> list[ServiceItemRead]:
    return await service.list_by_car(car_id, current_user.id)


@router.get("/{service_item_id}", response_model=ServiceItemRead, status_code=200)
async def get_service_item(
    service_item_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ServiceItemService = Depends(get_service_item_service),
) -> ServiceItemRead:
    return await service.get_service_item(service_item_id, current_user.id)


@router.patch("/{service_item_id}", response_model=ServiceItemRead, status_code=200)
async def update_service_item(
    service_item_id: UUID,
    update_schema: ServiceItemUpdate,
    current_user: User = Depends(get_current_user),
    service: ServiceItemService = Depends(get_service_item_service),
) -> ServiceItemRead:
    return await service.update_service_item(
        service_item_id, update_schema, current_user.id
    )


@router.post(
    "/{service_item_id}/mark-serviced", response_model=ServiceItemRead, status_code=200
)
async def mark_serviced(
    service_item_id: UUID,
    mark_schema: ServiceItemMarkServiced,
    current_user: User = Depends(get_current_user),
    service: ServiceItemService = Depends(get_service_item_service),
) -> ServiceItemRead:
    return await service.mark_serviced(service_item_id, mark_schema, current_user.id)


@router.delete("/{service_item_id}", status_code=204)
async def delete_service_item(
    service_item_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ServiceItemService = Depends(get_service_item_service),
) -> None:
    await service.delete_service_item(service_item_id, current_user.id)
