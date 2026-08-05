from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
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
):
    user_repo = UserRepository(session)
    auth_service = TelegramAuthService(session, user_repo)
    telegram_id = message.from_user.id

    if command.args:
        token = command.args.strip()
        try:
            result = await auth_service.link_user_by_token(token, telegram_id)
            if result:
                await message.answer(
                    "🎉 <b>Аккаунт успешно привязан!</b>\n\n"
                    "Теперь вы можете полноценно использовать Telegram Mini App и получать уведомления."
                )
            else:
                await message.answer(
                    "❌ <b>Недействительный токен привязки.</b>\n\n"
                    "Возможно, время действия ссылки истекло (5 минут). Сгенерируйте новую ссылку на сайте."
                )

        except TelegramAlreadyLinkedError:
            await message.answer("⚠️ Ваш профиль на сайте уже привязан к Telegram.")
        except TelegramAlreadyLinkedToAnotherError:
            await message.answer(
                "⚠️ Этот Telegram-аккаунт уже привязан к другому пользователю."
            )
        return

    user = await user_repo.get_by_telegram_id(telegram_id)

    if user:
        await message.answer(
            f"👋 <b>С возвращением, {message.from_user.first_name}!</b>\n\n"
            "Твой аккаунт привязан и готов к работе."
        )
    else:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Сайт приложения", url=settings.domain))
        await message.answer(
            f"👋 <b>Привет, {message.from_user.full_name}!</b>\n\n"
            "Чтобы начать пользоваться Car Minder:\n"
            "1. Зарегистрируйся на сайте приложения.\n"
            "2. Перейди в свой профиль и нажмите <b>«Привязать Telegram»</b>.",
            reply_markup=builder.as_markup(),
        )

    return
