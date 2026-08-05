import secrets

from aiogram.types import Update
from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status

from api.auth import ACCESS_TOKEN_COOKIE, CSRF_TOKEN_COOKIE, get_cookie_secure_flag
from api.deps import get_current_user, get_telegram_auth_service
from bot import bot, dp
from core.config import settings
from core.models import User
from core.schemas import TelegramAuthRequest, TelegramLinkTokenResponse, Token
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
) -> Token:
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
) -> dict:
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


@router.post("/link-token")
async def get_link_token(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: TelegramAuthService = Depends(get_telegram_auth_service),
) -> TelegramLinkTokenResponse:
    token = service.generate_link_token(current_user.id)
    bot_username = getattr(request.app.state, "bot_username", "carminder_bot")

    return TelegramLinkTokenResponse(
        token=token,
        bot_username=bot_username,
    )


@router.delete("/link", status_code=204)
async def unlink_telegram(
    current_user: User = Depends(get_current_user),
    service: TelegramAuthService = Depends(get_telegram_auth_service),
) -> None:
    telegram_id = current_user.telegram_id

    await service.unlink_telegram(current_user.id)

    if telegram_id:
        try:
            await bot.send_message(
                chat_id=telegram_id,
                text="⚠️ <b>Твой Telegram-аккаунт был отвязан от аккаунта приложения!</b>\n\nЕсли это сделал не ты, свяжитесь с поддержкой и смени пароль.",
            )
        except Exception as e:
            print(f"Failed to send unlink notification: {e}")


@router.get("/webhook")
async def get_bot_webhook() -> dict:
    return {"status": "Webhook is active"}
