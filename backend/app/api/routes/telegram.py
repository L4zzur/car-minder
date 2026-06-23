import secrets

from aiogram.types import Update
from bot import bot, dp
from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status

from api.auth import ACCESS_TOKEN_COOKIE, CSRF_TOKEN_COOKIE, get_cookie_secure_flag
from api.deps import get_telegram_auth_service
from core.config import settings
from core.schemas import TelegramAuthRequest, Token
from core.security import create_access_token
from services.telegram_auth import TelegramAuthService

router = APIRouter(
    prefix="/telegram",
    tags=["telegram"],
)


@router.post("/auth")
async def telegram_auth(
    response: Response,
    payload: TelegramAuthRequest,
    service: TelegramAuthService = Depends(get_telegram_auth_service),
):
    user = await service.authenticate_miniapp_user(payload)

    access_token = create_access_token(data={"sub": str(user.id)})
    csrf_token = secrets.token_urlsafe(32)
    cookie_secure = get_cookie_secure_flag()
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=access_token,
        httponly=True,
        secure=cookie_secure,
        samesite="lax",
        max_age=settings.auth.access_token_expire_minutes * 60,
        path="/",
    )
    response.set_cookie(
        key=CSRF_TOKEN_COOKIE,
        value=csrf_token,
        httponly=False,
        secure=cookie_secure,
        samesite="lax",
        max_age=settings.auth.access_token_expire_minutes * 60,
        path="/",
    )

    return Token(access_token=access_token, token_type="bearer")


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
