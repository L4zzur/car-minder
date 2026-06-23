import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from bot import bot, dp
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middleware.csrf import csrf_protect

from api.errors import register_exception_handlers
from api.router import api_router
from core.config import settings
from core.db_helper import db_helper


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Setting webhook to: {settings.bot.webhook_url}")

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(
        url=settings.bot.webhook_url,
        allowed_updates=dp.resolve_used_update_types(),
        secret_token=settings.bot.webhook_secret.get_secret_value(),
    )

    print("Bot started")
    # startup
    yield
    # shutdown
    await bot.delete_webhook()
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
