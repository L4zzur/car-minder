from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User
from core.schemas.user import UserCreate, UserRead, UserUpdate
from core.security import hash_password, verify_password
from repositories import UserRepository

from .exceptions import (
    EmailAlreadyTakenError,
    InvalidCurrentPasswordError,
    UsernameAlreadyTakenError,
    UserNotFoundError,
)


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

        if create_schema.email:
            _email_user = await self.user_repository.get_by_email(create_schema.email)
            if _email_user:
                raise EmailAlreadyTakenError(create_schema.email)

        user = User(
            username=create_schema.username,
            name=create_schema.name,
            email=create_schema.email,
            hashed_password=hash_password(create_schema.password),
        )

        await self.user_repository.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return UserRead.model_validate(user)

    async def authenticate_user(
        self,
        username: str,
        password: str,
    ) -> User | None:
        user = await self.user_repository.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def get_user_model_by_id(
        self,
        id: UUID,
    ) -> User | None:
        return await self.user_repository.get_by_id(id)

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

        if update_schema.email and update_schema.email != user.email:
            existing = await self.user_repository.get_by_email(update_schema.email)
            if existing and existing.id != user_id:
                raise EmailAlreadyTakenError(update_schema.email)

        update_data = update_schema.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.session.commit()
        await self.session.refresh(user)

        return UserRead.model_validate(user)

    async def change_password(
        self,
        user_id: UUID,
        current_password: str,
        new_password: str,
    ) -> None:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(user_id)

        if not verify_password(current_password, user.hashed_password):
            raise InvalidCurrentPasswordError()

        user.hashed_password = hash_password(new_password)
        await self.session.commit()

    async def delete_user(
        self,
        user_id: UUID,
    ) -> None:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(user_id)

        await self.user_repository.delete(user)
        await self.session.commit()
