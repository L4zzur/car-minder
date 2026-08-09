from typing import cast

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from core.schemas import Language, UserSettingsUpdate
from repositories import UserRepository, UserSettingsRepository
from services.user_settings import UserSettingsService

router = Router()

LANGUAGE_NAMES = {
    "ru": "Русский",
    "en": "English",
}


@router.message(Command("language", "lang"))
async def cmd_language(message: Message, i18n: I18nContext) -> None:
    builder = InlineKeyboardBuilder()
    builder.button(text=i18n.get("language_name_ru"), callback_data="set_language:ru")
    builder.button(text=i18n.get("language_name_en"), callback_data="set_language:en")
    builder.adjust(1)
    await message.answer(i18n.get("language_prompt"), reply_markup=builder.as_markup())


@router.callback_query(F.data.in_({"set_language:ru", "set_language:en"}))
async def on_language_selected(
    callback: CallbackQuery,
    i18n: I18nContext,
    session: AsyncSession,
) -> None:
    if not callback.data or not callback.message:
        return
    locale = cast(Language, callback.data.split(":", 1)[1])

    user = await UserRepository(session).get_by_telegram_id(callback.from_user.id)
    if user is None:
        await callback.answer(i18n.get("language_not_linked"), show_alert=True)
        return

    settings_service = UserSettingsService(session, UserSettingsRepository(session))
    await settings_service.update_settings(user.id, UserSettingsUpdate(language=locale))

    with i18n.use_locale(locale):
        text = i18n.get("language_changed", language=LANGUAGE_NAMES[locale])
    await callback.message.answer(text)
    await callback.answer()
