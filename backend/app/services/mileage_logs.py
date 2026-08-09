from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from core.models import MileageLog
from core.schemas import MileageLogCreate, MileageLogRead
from repositories import (
    CarRepository,
    MileageLogRepository,
    UserSettingsRepository,
)
from rules import validate_new_mileage_log_odometer
from services.scheduler_helper import sync_mileage_prompt_job

from .exceptions import CarNotFoundError, MileageLogNotFoundError


class MileageLogService:
    def __init__(
        self,
        session: AsyncSession,
        car_repository: CarRepository,
        mileage_log_repository: MileageLogRepository,
    ) -> None:
        self.session = session
        self.car_repository = car_repository
        self.mileage_log_repository = mileage_log_repository

    async def add_mileage(
        self,
        create_schema: MileageLogCreate,
        user_id: UUID,
    ) -> MileageLogRead:
        car = await self.car_repository.get_by_id(create_schema.car_id)
        if car is None or car.user_id != user_id:
            raise CarNotFoundError(create_schema.car_id)

        # Validating odometer
        latest_mileage = await self.mileage_log_repository.get_latest_for_car(
            create_schema.car_id
        )
        current_odometer_km = (
            latest_mileage.odometer_km
            if latest_mileage is not None
            else car.initial_odometer_km
        )
        validate_new_mileage_log_odometer(
            current_odometer_km=current_odometer_km,
            new_odometer_km=create_schema.odometer_km,
        )

        mileage_log = MileageLog(
            car_id=create_schema.car_id,
            odometer_km=create_schema.odometer_km,
        )

        await self.mileage_log_repository.add(mileage_log)
        await self.session.commit()
        await self.session.refresh(mileage_log)

        # Re-sync odometer prompt job to reset the inactivity timer
        settings_repo = UserSettingsRepository(self.session)
        user_settings = await settings_repo.get_by_user_id(user_id)
        sync_mileage_prompt_job(car, mileage_log.created_at, user_settings)

        return MileageLogRead.model_validate(mileage_log)

    async def list_by_car(
        self,
        car_id: UUID,
        user_id: UUID,
    ) -> list[MileageLogRead]:
        _car = await self.car_repository.get_by_id(car_id)
        if _car is None or _car.user_id != user_id:
            raise CarNotFoundError(car_id)

        mileage_logs = await self.mileage_log_repository.list_by_car_id(car_id)
        return [
            MileageLogRead.model_validate(mileage_log) for mileage_log in mileage_logs
        ]

    async def delete_mileage(
        self,
        mileage_id: UUID,
        user_id: UUID,
    ) -> None:
        mileage_log = await self.mileage_log_repository.get_by_id(mileage_id)
        if mileage_log is None:
            raise MileageLogNotFoundError(mileage_id)

        car = await self.car_repository.get_by_id(mileage_log.car_id)
        if car is None or car.user_id != user_id:
            raise CarNotFoundError(mileage_log.car_id)

        await self.mileage_log_repository.delete(mileage_log)
        await self.session.commit()
