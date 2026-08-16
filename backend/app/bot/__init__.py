from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import (
    BotCommand,
    BotCommandScopeDefault,
    MenuButtonDefault,
    MenuButtonWebApp,
    WebAppInfo,
)
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores.fluent_compile_core import FluentCompileCore

from bot.middlewares import DbLocaleManager, DbSessionMiddleware
from core.config import settings
from core.logger import logger

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


async def setup_bot_ui() -> None:
    if not bot:
        return

    mini_app_url = settings.bot.mini_app_url
    if mini_app_url:
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="сar minder",
                web_app=WebAppInfo(url=mini_app_url),
            )
        )
    else:
        await bot.set_chat_menu_button(menu_button=MenuButtonDefault())

    commands_ru = [
        BotCommand(command="start", description=i18n_core.get("bot_cmd_start", "ru")),
        BotCommand(command="app", description=i18n_core.get("bot_cmd_app", "ru")),
        BotCommand(
            command="language", description=i18n_core.get("bot_cmd_language", "ru")
        ),
    ]
    commands_en = [
        BotCommand(command="start", description=i18n_core.get("bot_cmd_start", "en")),
        BotCommand(command="app", description=i18n_core.get("bot_cmd_app", "en")),
        BotCommand(
            command="language", description=i18n_core.get("bot_cmd_language", "en")
        ),
    ]

    try:
        await bot.set_my_commands(
            commands_ru, scope=BotCommandScopeDefault(), language_code="ru"
        )
        await bot.set_my_commands(
            commands_en, scope=BotCommandScopeDefault(), language_code="en"
        )
        await bot.set_my_commands(commands_en, scope=BotCommandScopeDefault())
    except Exception as e:
        logger.warning(f"Failed to set bot commands: {e}")
