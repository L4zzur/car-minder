from uuid import UUID

from fastapi import APIRouter, Depends

from api.deps import get_car_service, get_current_user
from core.models import User
from core.schemas import CarCreate, CarRead, CarUpdate
from services import CarService
from services.exceptions import CarNotFoundError

router = APIRouter(prefix="/cars", tags=["cars"])


@router.post("", response_model=CarRead, status_code=201)
async def add_car(
    create_schema: CarCreate,
    current_user: User = Depends(get_current_user),
    service: CarService = Depends(get_car_service),
) -> CarRead:
    return await service.add_car(create_schema, current_user.id)


@router.get("", response_model=list[CarRead], status_code=200)
async def list_user_cars(
    current_user: User = Depends(get_current_user),
    service: CarService = Depends(get_car_service),
) -> list[CarRead]:
    return await service.list_user_cars(current_user.id)


@router.get("/{car_id}", response_model=CarRead, status_code=200)
async def get_car(
    car_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CarService = Depends(get_car_service),
) -> CarRead:
    car = await service.get_car(car_id, current_user.id)
    if car is None:
        raise CarNotFoundError(car_id)
    return car


@router.patch("/{car_id}", response_model=CarRead, status_code=200)
async def update_car(
    car_id: UUID,
    update_schema: CarUpdate,
    current_user: User = Depends(get_current_user),
    service: CarService = Depends(get_car_service),
) -> CarRead:
    return await service.update_car(car_id, update_schema, current_user.id)


@router.delete("/{car_id}", status_code=204)
async def delete_car(
    car_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CarService = Depends(get_car_service),
) -> None:
    await service.delete_car(car_id, current_user.id)
