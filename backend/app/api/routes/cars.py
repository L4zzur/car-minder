from uuid import UUID

from fastapi import APIRouter, Depends

from api.deps import get_car_service
from core.schemas import CarCreate, CarRead, CarUpdate
from services import CarService
from services.exceptions import CarNotFoundError

router = APIRouter(prefix="/cars", tags=["cars"])


@router.post("", response_model=CarRead, status_code=201)
async def add_car(
    create_schema: CarCreate,
    service: CarService = Depends(get_car_service),
) -> CarRead:
    return await service.add_car(create_schema)


@router.get("/user/{user_id}", response_model=list[CarRead], status_code=200)
async def list_user_cars(
    user_id: UUID,
    service: CarService = Depends(get_car_service),
) -> list[CarRead]:
    return await service.list_user_cars(user_id)


@router.get("/{car_id}", response_model=CarRead, status_code=200)
async def get_car(
    car_id: UUID,
    service: CarService = Depends(get_car_service),
) -> CarRead:
    car = await service.get_car(car_id)
    if car is None:
        raise CarNotFoundError(car_id)
    return car


@router.patch("/{car_id}", response_model=CarRead, status_code=200)
async def update_car(
    car_id: UUID,
    update_schema: CarUpdate,
    service: CarService = Depends(get_car_service),
) -> CarRead:
    return await service.update_car(car_id, update_schema)


@router.delete("/{car_id}", status_code=204)
async def delete_car(
    car_id: UUID,
    service: CarService = Depends(get_car_service),
) -> None:
    await service.delete_car(car_id)
