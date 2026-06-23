from secrets import token_urlsafe

from aiogram.utils.web_app import safe_parse_webapp_init_data
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import User
from core.schemas import TelegramAuthRequest, UserRead
from core.security import hash_password
from repositories import UserRepository


class TelegramAuthService:
    def __init__(self, session: AsyncSession, user_repository: UserRepository) -> None:
        self.session = session
        self.user_repository = user_repository

    async def authenticate_miniapp_user(
        self, tg_auth_request: TelegramAuthRequest
    ) -> UserRead:
        web_app_data = safe_parse_webapp_init_data(
            token=settings.bot.token.get_secret_value(),
            init_data=tg_auth_request.init_data_raw,
        )

        user = await self.user_repository.get_by_telegram_id(web_app_data.user.id)
        if user:
            return UserRead.model_validate(user)

        user = User(
            telegram_id=web_app_data.user.id,
            username=f"tg_{web_app_data.user.id}",
            name=web_app_data.user.first_name,
            hashed_password=hash_password(token_urlsafe(24)),
        )

        await self.user_repository.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return UserRead.model_validate(user)
