from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import CreatedAtMixin, IdMixin, UpdatedAtMixin

if TYPE_CHECKING:
    from .car import Car


class User(Base, IdMixin, CreatedAtMixin, UpdatedAtMixin):
    telegram_id: Mapped[int | None] = mapped_column(
        BigInteger,
        unique=True,
        nullable=True,
        comment="User Telegram ID",
    )

    username: Mapped[str] = mapped_column(
        unique=True,
        nullable=False,
        comment="User display username",
    )

    email: Mapped[str | None] = mapped_column(
        unique=True,
        nullable=True,
        comment="User email address",
    )

    hashed_password: Mapped[str] = mapped_column(
        nullable=False,
        comment="Password hash",
    )

    name: Mapped[str] = mapped_column(
        nullable=False,
        comment="User display name",
    )

    cars: Mapped[list["Car"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        CheckConstraint("length(trim(username)) > 0", name="user_username_not_blank"),
        CheckConstraint("length(trim(name)) > 0", name="user_name_not_blank"),
    )
