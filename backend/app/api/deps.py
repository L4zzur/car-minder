from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.db_helper import db_helper
from core.models import User
from core.schemas import TokenData
from core.security import decode_access_token
from repositories import (
    CarRepository,
    MileageLogRepository,
    ServiceItemRepository,
    UserRepository,
)
from repositories.reminder import ReminderRepository
from services import CarService, MileageLogService, ServiceItemService, UserService
from services.reminders import ReminderService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api.prefix}/auth/login")


async def get_user_service(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> UserService:
    return UserService(
        session=session,
        user_repository=UserRepository(session),
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    id: str | None = payload.get("sub")
    if id is None:
        raise credentials_exception

    token_data = TokenData(id=id)
    user = await user_service.get_user_model_by_id(token_data.id)

    if user is None:
        raise credentials_exception
    return user


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
