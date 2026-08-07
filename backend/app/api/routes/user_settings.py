from fastapi import APIRouter, Depends

from api.deps import get_current_user, get_user_settings_service
from core.models import User
from core.schemas import UserSettingsRead, UserSettingsUpdate
from services import UserSettingsService

router = APIRouter(prefix="/users/me/settings", tags=["user_settings"])


@router.get("", response_model=UserSettingsRead, status_code=200)
async def get_my_settings(
    current_user: User = Depends(get_current_user),
    service: UserSettingsService = Depends(get_user_settings_service),
) -> UserSettingsRead:
    return await service.get_settings(current_user.id)


@router.patch("", response_model=UserSettingsRead, status_code=200)
async def update_my_settings(
    update_schema: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    service: UserSettingsService = Depends(get_user_settings_service),
) -> UserSettingsRead:
    return await service.update_settings(current_user.id, update_schema)
