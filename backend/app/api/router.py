from fastapi import APIRouter

from api.routes import (
    auth_router,
    cars_router,
    mileage_logs_router,
    reminders_router,
    service_items_router,
    telegram_router,
    user_settings_router,
    users_router,
)
from core.config import settings

api_router = APIRouter(prefix=settings.api.prefix)

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(user_settings_router)
api_router.include_router(cars_router)
api_router.include_router(mileage_logs_router)
api_router.include_router(service_items_router)
api_router.include_router(reminders_router)
api_router.include_router(telegram_router)
