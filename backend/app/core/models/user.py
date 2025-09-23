from typing import TYPE_CHECKING

from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.mixins import CreatedAtMixin, UpdatedAtMixin

from .base import Base

if TYPE_CHECKING:
    from .car import Car


class User(Base, CreatedAtMixin, UpdatedAtMixin):
    tg_id: Mapped[int] = mapped_column(
        primary_key=True,
        unique=True,
        nullable=False,
        comment="Telegram user ID",
    )

    name: Mapped[str] = mapped_column(
        nullable=False,
        comment="Telegram first name",
    )

    username: Mapped[str | None] = mapped_column(
        nullable=True,
        comment="Telegram username",
    )

    is_premium: Mapped[bool] = mapped_column(
        nullable=False,
        server_default=text("FALSE"),
        comment="Has the user bought a premium",
    )

    cars: Mapped[list["Car"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
