from datetime import time
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import CreatedAtMixin, IdMixin, UpdatedAtMixin

if TYPE_CHECKING:
    from .user import User


class UserSettings(Base, IdMixin, CreatedAtMixin, UpdatedAtMixin):
    __tablename__ = "user_settings"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        comment="ID of the user",
    )

    user: Mapped["User"] = relationship(back_populates="settings")

    service_reminder_time: Mapped[time] = mapped_column(
        nullable=False,
        server_default=text("'12:00:00'"),
        comment="Preferred time of day for service reminders",
    )

    mileage_reminder_time: Mapped[time] = mapped_column(
        nullable=False,
        server_default=text("'19:00:00'"),
        comment="Preferred time of day for mileage prompts",
    )

    mileage_prompt_interval_days: Mapped[int | None] = mapped_column(
        nullable=True,
        default=14,
        server_default=text("14"),
        comment="Interval in days to prompt user for mileage update",
    )

    timezone: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="Europe/Moscow",
        server_default=text("'Europe/Moscow'"),
        comment="User timezone name",
    )

    notify_via_telegram: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
        server_default=text("TRUE"),
        comment="Enable notifications via Telegram",
    )

    notify_via_email: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
        server_default=text("FALSE"),
        comment="Enable notifications via Email",
    )

    language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="ru",
        server_default=text("'ru'"),
        comment="User preferred language (ru/en)",
    )
