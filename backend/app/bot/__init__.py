from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores.fluent_compile_core import FluentCompileCore
from bot.middlewares import DbLocaleManager, DbSessionMiddleware
from core.config import settings

from .handlers import router as bot_router

LOCALES_PATH = Path(__file__).resolve().parent / "locales" / "{locale}" / "LC_MESSAGES"

if settings.bot.is_active and settings.bot.token:
    bot: Bot | None = Bot(
        token=settings.bot.token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
else:
    bot = None

dp = Dispatcher()
dp.include_router(bot_router)

# Order matters:
# DbSessionMiddleware must run before I18nMiddleware so that
# the locale manager can read the user's language from the database
dp.update.outer_middleware(DbSessionMiddleware())

i18n_core = FluentCompileCore(path=LOCALES_PATH, default_locale="ru")
i18n_middleware = I18nMiddleware(
    core=i18n_core,
    manager=DbLocaleManager(default_locale="ru"),
    default_locale="ru",
)
i18n_middleware.setup(dp)
