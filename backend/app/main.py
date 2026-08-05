from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.errors import register_exception_handlers
from api.router import api_router
from bot import bot, dp
from core.config import settings
from core.db_helper import db_helper
from middleware.csrf import csrf_protect


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.bot.is_active and bot:
        try:
            print(f"Setting webhook to: {settings.bot.webhook_url}")
            await bot.delete_webhook(drop_pending_updates=True)
            webhook_url = settings.bot.webhook_url
            if webhook_url:
                secret_token = (
                    settings.bot.webhook_secret.get_secret_value()
                    if settings.bot.webhook_secret
                    else None
                )
                await bot.set_webhook(
                    url=webhook_url,
                    allowed_updates=dp.resolve_used_update_types(),
                    secret_token=secret_token,
                )
            bot_info = await bot.get_me()
            app.state.bot_username = bot_info.username
            print(f"Bot started: @{bot_info.username}")
        except Exception as e:
            print(f"Failed to initialize Telegram Bot: {e}")
            app.state.bot_username = None
    else:
        print("Telegram bot is disabled.")
        app.state.bot_username = None

    # startup
    yield
    # shutdown
    if settings.bot.is_active and bot:
        try:
            await bot.delete_webhook()
        except Exception:
            pass
    await db_helper.dispose()


app = FastAPI(
    title="Car Minder API",
    version="0.0.1",
    lifespan=lifespan,
)

app.middleware("http")(csrf_protect)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


register_exception_handlers(app)
app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
