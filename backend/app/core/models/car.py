from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ColumnElement, ForeignKey, func, select
from sqlalchemy.ext import hybrid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import CreatedAtMixin, IdMixin, UpdatedAtMixin

if TYPE_CHECKING:
    from .mileage_log import MileageLog
    from .reminder import Reminder
    from .service_item import ServiceItem
    from .user import User


class Car(Base, IdMixin, CreatedAtMixin, UpdatedAtMixin):
    user_tg_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.tg_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
        comment="Telegram ID of the user",
    )

    user: Mapped["User"] = relationship(back_populates="cars", passive_deletes=True)

    brand: Mapped[str] = mapped_column(
        nullable=False,
        comment="Car brand",
    )

    model: Mapped[str] = mapped_column(
        nullable=False,
        comment="Car model",
    )

    year: Mapped[int] = mapped_column(
        nullable=False,
        comment="Car year",
    )

    first_mileage: Mapped[int] = mapped_column(
        nullable=False,
        comment="First mileage at adding to the bot",
    )

    mileage_logs: Mapped[list["MileageLog"]] = relationship(
        back_populates="car",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    reminders: Mapped[list["Reminder"]] = relationship(
        back_populates="car",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    service_items: Mapped[list["ServiceItem"]] = relationship(
        back_populates="car",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Python-level derived field
    @hybrid.hybrid_property
    def mileage(self) -> int:
        """Current mileage of the car (derived from logs or initial value)."""
        if not self.mileage_logs:
            return self.first_mileage
        return max(log.mileage for log in self.mileage_logs)

    # SQL-level derived field
    @mileage.inplace.expression
    @classmethod
    def _mileage_expression(cls) -> ColumnElement[int]:
        """SQL expression to compute current mileage."""
        from .mileage_log import MileageLog

        return (
            select(func.coalesce(func.max(MileageLog.mileage), cls.first_mileage))
            .where(MileageLog.car_id == cls.id)
            .scalar_subquery()
        )

    __table_args__ = (
        CheckConstraint(
            "year >= 1930 AND year <= CAST(strftime('%Y','now') AS INTEGER)",
            name="car_year_valid",
        ),
    )
