from aiogram import Router, html
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from repositories import UserRepository
from services.exceptions import (
    TelegramAlreadyLinkedError,
    TelegramAlreadyLinkedToAnotherError,
)
from services.telegram_auth import TelegramAuthService

router = Router()


@router.message(Command("start"))
async def cmd_start(
    message: Message,
    command: CommandObject,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    if not message.from_user:
        return
    user_repo = UserRepository(session)
    auth_service = TelegramAuthService(session, user_repo)
    telegram_id = message.from_user.id

    if command.args:
        token = command.args.strip()
        try:
            result = await auth_service.link_user_by_token(token, telegram_id)
            if result:
                await message.answer(i18n.get("start_linked_success"))
            else:
                await message.answer(i18n.get("start_invalid_token"))

        except TelegramAlreadyLinkedError:
            await message.answer(i18n.get("start_already_linked"))
        except TelegramAlreadyLinkedToAnotherError:
            await message.answer(i18n.get("start_already_linked_to_another"))
        return

    user = await user_repo.get_by_telegram_id(telegram_id)

    if user:
        await message.answer(
            i18n.get(
                "start_welcome_back",
                name=html.quote(user.name),
            )
        )
    else:
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text=i18n.get("site_button"), url=settings.domain)
        )
        await message.answer(
            i18n.get("start_hello_new", name=html.quote(message.from_user.full_name)),
            reply_markup=builder.as_markup(),
        )

    return
