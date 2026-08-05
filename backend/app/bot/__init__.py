from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

from bot.middlewares import DbSessionMiddleware
from core.config import settings

from .handlers import router as bot_router

if settings.bot.is_active and settings.bot.token:
    bot: Bot | None = Bot(
        token=settings.bot.token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
else:
    bot = None

dp = Dispatcher()
dp.include_router(bot_router)
dp.update.middleware(DbSessionMiddleware())
dp.callback_query.middleware(DbSessionMiddleware())
