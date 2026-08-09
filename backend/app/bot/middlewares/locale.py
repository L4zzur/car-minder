from typing import Any, cast

from aiogram.types import TelegramObject, Update, User
from aiogram.types.update import UpdateTypeLookupError
from aiogram_i18n.managers.base import BaseManager

from repositories import UserRepository, UserSettingsRepository

AVAILABLE_LOCALES = ("ru", "en")


def _extract_from_user(event: TelegramObject) -> User | None:
    if isinstance(event, Update):
        try:
            event = event.event
        except UpdateTypeLookupError:
            return None
    return getattr(event, "from_user", None)


class DbLocaleManager(BaseManager):
    async def get_locale(self, event: TelegramObject, **kwargs: Any) -> str:
        session = kwargs.get("session")
        from_user = _extract_from_user(event)
        telegram_id = from_user.id if from_user is not None else None

        if session is not None and telegram_id is not None:
            user = await UserRepository(session).get_by_telegram_id(telegram_id)
            if user is not None:
                settings = await UserSettingsRepository(session).get_by_user_id(user.id)
                if settings is not None and settings.language in AVAILABLE_LOCALES:
                    return settings.language

        if from_user is not None:
            code = (from_user.language_code or "")[:2]
            if code in AVAILABLE_LOCALES:
                return code

        return cast(str, self.default_locale)

    async def set_locale(self, *args: Any, **kwargs: Any) -> None:
        return None
