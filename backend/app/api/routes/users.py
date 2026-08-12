from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from api.deps import get_current_user, get_user_service
from core.config import settings
from core.models import User
from core.schemas import UserCreate, UserRead, UserUpdate
from services import UserService
from services.exceptions import UserNotFoundError

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=201)
async def register_user(
    create_schema: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    if not settings.auth.allow_signup:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is disabled",
        )
    return await service.register_user(create_schema)


@router.get("/u/{username}", response_model=UserRead, status_code=200)
async def get_user_by_username(
    username: str,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    user = await service.get_user_by_username(username)
    if user is None:
        raise UserNotFoundError()
    return user


@router.get("/{user_id}", response_model=UserRead, status_code=200)
async def get_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    user = await service.get_user(user_id)
    if user is None:
        raise UserNotFoundError(user_id)
    return user


@router.patch("/{user_id}", response_model=UserRead, status_code=200)
async def update_user(
    user_id: UUID,
    update_schema: UserUpdate,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserRead:
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return await service.update_user(user_id, update_schema)


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> None:
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    await service.delete_user(user_id)
