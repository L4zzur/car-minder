__all__ = [
    "cars_router",
    "mileage_logs_router",
    "reminders_router",
    "service_items_router",
    "users_router",
    "auth_router",
    "telegram_router",
]

from .auth import router as auth_router
from .cars import router as cars_router
from .mileage_logs import router as mileage_logs_router
from .reminders import router as reminders_router
from .service_items import router as service_items_router
from .telegram import router as telegram_router
from .users import router as users_router
