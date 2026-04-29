from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User
from core.schemas.user import UserCreate, UserRead, UserUpdate
from repositories import UserRepository

from .exceptions import UsernameAlreadyTakenError, UserNotFoundError


class UserService:
    def __init__(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
    ) -> None:
        self.session = session
        self.user_repository = user_repository

    async def register_user(
        self,
        create_schema: UserCreate,
    ) -> UserRead:
        _user = await self.user_repository.get_by_username(create_schema.username)
        if _user:
            raise UsernameAlreadyTakenError(create_schema.username)

        user = User(
            username=create_schema.username,
            name=create_schema.name,
        )

        await self.user_repository.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return UserRead.model_validate(user)

    async def get_user(
        self,
        user_id: UUID,
    ) -> UserRead | None:
        user = await self.user_repository.get_by_id(user_id)
        return UserRead.model_validate(user) if user else None

    async def get_user_by_username(
        self,
        username: str,
    ) -> UserRead | None:
        user = await self.user_repository.get_by_username(username)
        return UserRead.model_validate(user) if user else None

    async def update_user(
        self,
        user_id: UUID,
        update_schema: UserUpdate,
    ) -> UserRead:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(user_id)

        update_data = update_schema.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.session.commit()
        await self.session.refresh(user)

        return UserRead.model_validate(user)

    async def delete_user(
        self,
        user_id: UUID,
    ) -> None:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(user_id)

        await self.user_repository.delete(user)
        await self.session.commit()
