from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.db_helper import db_helper
from repositories import (
    CarRepository,
    MileageLogRepository,
    ServiceItemRepository,
    UserRepository,
)
from repositories.reminder import ReminderRepository
from services import CarService, MileageLogService, ServiceItemService, UserService
from services.reminders import ReminderService


async def get_user_service(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> UserService:
    return UserService(
        session=session,
        user_repository=UserRepository(session),
    )


async def get_car_service(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> CarService:
    return CarService(
        session=session,
        car_repository=CarRepository(session),
        user_repository=UserRepository(session),
    )


async def get_mileage_log_service(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> MileageLogService:
    return MileageLogService(
        session=session,
        mileage_log_repository=MileageLogRepository(session),
        car_repository=CarRepository(session),
    )


async def get_service_item_service(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> ServiceItemService:
    return ServiceItemService(
        session=session,
        service_item_repository=ServiceItemRepository(session),
        car_repository=CarRepository(session),
        mileage_log_repository=MileageLogRepository(session),
    )


async def get_reminder_service(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> ReminderService:
    return ReminderService(
        session=session,
        reminder_repository=ReminderRepository(session),
        service_item_repository=ServiceItemRepository(session),
    )
