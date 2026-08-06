import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from aiogram.utils.web_app import safe_parse_webapp_init_data
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import User
from core.schemas import TelegramAuthRequest, UserRead
from repositories import UserRepository
from services.exceptions import (
    TelegramAlreadyLinkedError,
    TelegramAlreadyLinkedToAnotherError,
    TelegramNotLinkedError,
    UserNotFoundError,
)


class TelegramAuthService:
    _link_tokens: dict[str, tuple[UUID, datetime]] = {}

    def __init__(self, session: AsyncSession, user_repository: UserRepository) -> None:
        self.session = session
        self.user_repository = user_repository

    async def authenticate_miniapp_user(
        self, tg_auth_request: TelegramAuthRequest
    ) -> UserRead:
        if not settings.bot.is_active or not settings.bot.token:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Telegram bot is disabled",
            )
        try:
            web_app_data = safe_parse_webapp_init_data(
                token=settings.bot.token.get_secret_value(),
                init_data=tg_auth_request.init_data_raw,
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
            )

        if not web_app_data.user:
            raise UserNotFoundError()
        user = await self.user_repository.get_by_telegram_id(web_app_data.user.id)
        if not user:
            raise UserNotFoundError()

        return UserRead.model_validate(user)

    def generate_link_token(self, user_id: UUID) -> str:
        token = secrets.token_urlsafe(12)
        expires_at = datetime.now(UTC) + timedelta(minutes=5)
        self._link_tokens[token] = (user_id, expires_at)
        return token

    def resolve_link_token(self, token: str) -> UUID | None:
        token_data = self._link_tokens.get(token)
        if not token_data:
            return None

        user_id, expires_at = token_data
        del self._link_tokens[token]

        if datetime.now(UTC) > expires_at:
            return None

        return user_id

    async def link_user_by_token(self, token: str, telegram_id: int) -> bool:
        user_id = self.resolve_link_token(token)
        if not user_id:
            return False

        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return False

        if user.telegram_id:
            raise TelegramAlreadyLinkedError(telegram_id)
        if await self.user_repository.get_by_telegram_id(telegram_id):
            raise TelegramAlreadyLinkedToAnotherError(telegram_id)

        user.telegram_id = telegram_id
        await self.session.commit()
        await self.session.refresh(user)
        return True

    async def unlink_telegram(self, user_id: UUID) -> User:
        user = await self.user_repository.get_by_id(user_id)
        if not user or not user.telegram_id:
            raise TelegramNotLinkedError(user_id)

        user.telegram_id = None
        await self.session.commit()
        await self.session.refresh(user)
        return user
