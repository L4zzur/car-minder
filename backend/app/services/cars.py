from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Car
from core.schemas import CarCreate, CarRead, CarUpdate
from repositories import CarRepository, UserRepository

from .exceptions import CarNotFoundError, UserNotFoundError


class CarService:
    def __init__(
        self,
        session: AsyncSession,
        car_repository: CarRepository,
        user_repository: UserRepository,
    ) -> None:
        self.session = session
        self.car_repository = car_repository
        self.user_repository = user_repository

    async def add_car(
        self,
        create_schema: CarCreate,
        user_id: UUID,
    ) -> CarRead:
        _user = await self.user_repository.get_by_id(user_id)
        if _user is None:
            raise UserNotFoundError(user_id)

        car = Car(
            user_id=user_id,
            brand=create_schema.brand,
            model=create_schema.model,
            year=create_schema.year,
            initial_odometer_km=create_schema.initial_odometer_km,
        )

        await self.car_repository.add(car)
        await self.session.commit()
        await self.session.refresh(car)

        return CarRead.model_validate(car)

    async def get_car(
        self,
        car_id: UUID,
        user_id: UUID,
    ) -> CarRead:
        car = await self.car_repository.get_by_id(car_id)
        if car is None or car.user_id != user_id:
            raise CarNotFoundError(car_id)
        return CarRead.model_validate(car)

    async def list_user_cars(
        self,
        user_id: UUID,
    ) -> list[CarRead]:
        _user = await self.user_repository.get_by_id(user_id)
        if _user is None:
            raise UserNotFoundError(user_id)

        cars = await self.car_repository.list_by_user_id(user_id)
        return [CarRead.model_validate(car) for car in cars]

    async def update_car(
        self,
        car_id: UUID,
        update_schema: CarUpdate,
        user_id: UUID,
    ) -> CarRead:
        car = await self.car_repository.get_by_id(car_id)
        if car is None or car.user_id != user_id:
            raise CarNotFoundError(car_id)

        update_data = update_schema.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(car, field, value)

        await self.session.commit()
        await self.session.refresh(car)

        return CarRead.model_validate(car)

    async def delete_car(
        self,
        car_id: UUID,
        user_id: UUID,
    ) -> None:
        car = await self.car_repository.get_by_id(car_id)
        if car is None or car.user_id != user_id:
            raise CarNotFoundError(car_id)

        await self.car_repository.delete(car)
        await self.session.commit()
