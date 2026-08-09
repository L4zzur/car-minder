from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Car
from core.schemas import CarCreate, CarRead, CarUpdate
from repositories import (
    CarRepository,
    MileageLogRepository,
    UserRepository,
    UserSettingsRepository,
)
from services.scheduler_helper import (
    remove_mileage_prompt_job,
    sync_mileage_prompt_job,
)

from .exceptions import CarNotFoundError, UserNotFoundError


class CarService:
    def __init__(
        self,
        session: AsyncSession,
        car_repository: CarRepository,
        mileage_log_repository: MileageLogRepository,
        user_repository: UserRepository,
    ) -> None:
        self.session = session
        self.car_repository = car_repository
        self.mileage_log_repository = mileage_log_repository
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

        user_settings = await UserSettingsRepository(self.session).get_by_user_id(
            user_id
        )
        sync_mileage_prompt_job(car, car.created_at, user_settings)

        return await self._to_read_schema(car)

    async def get_car(
        self,
        car_id: UUID,
        user_id: UUID,
    ) -> CarRead:
        car = await self.car_repository.get_by_id(car_id)
        if car is None or car.user_id != user_id:
            raise CarNotFoundError(car_id)
        return await self._to_read_schema(car)

    async def list_user_cars(
        self,
        user_id: UUID,
    ) -> list[CarRead]:
        _user = await self.user_repository.get_by_id(user_id)
        if _user is None:
            raise UserNotFoundError(user_id)

        cars = await self.car_repository.list_by_user_id(user_id)
        return [await self._to_read_schema(car) for car in cars]

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

        return await self._to_read_schema(car)

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

        remove_mileage_prompt_job(car_id)

    async def _to_read_schema(self, car: Car) -> CarRead:
        latest_mileage = await self.mileage_log_repository.get_latest_for_car(car.id)
        current_odometer_km = (
            latest_mileage.odometer_km
            if latest_mileage is not None
            else car.initial_odometer_km
        )

        return CarRead(
            id=car.id,
            user_id=car.user_id,
            brand=car.brand,
            model=car.model,
            year=car.year,
            initial_odometer_km=car.initial_odometer_km,
            current_odometer_km=current_odometer_km,
            created_at=car.created_at,
            updated_at=car.updated_at,
        )
