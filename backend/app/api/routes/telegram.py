import secrets

from aiogram.types import Update
from bot import bot, dp
from fastapi import APIRouter, Header, HTTPException, Request, Response, status

from core.config import settings

router = APIRouter(
    prefix="/telegram",
)


@router.post("/webhook")
async def bot_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str = Header(
        None, alias="X-Telegram-Bot-Api-Secret-Token"
    ),
):
    if (
        x_telegram_bot_api_secret_token
        != settings.bot.webhook_secret.get_secret_value()
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Secret Token"
        )

    update_data = await request.json()
    try:
        update = Update.model_validate(update_data, context={"bot": bot})
        await dp.feed_update(bot, update)
    except Exception as e:
        print(f"Update error: {e}")

    return {"ok": True}


@router.get("/webhook")
async def get_bot_webhook():
    return {"status": "Webhook is active"}
