from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.mixins import CreatedAtMixin, IdMixin, UpdatedAtMixin

from .base import Base

if TYPE_CHECKING:
    from .car import Car
    from .service_item import ServiceItem


class Reminder(Base, IdMixin, CreatedAtMixin, UpdatedAtMixin):
    car_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "cars.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        comment="ID of the car",
    )

    car: Mapped["Car"] = relationship(back_populates="reminders")

    service_item_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "service_items.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        comment="ID of the service item",
    )

    service_item: Mapped["ServiceItem"] = relationship(back_populates="reminders")

    is_active: Mapped[bool] = mapped_column(
        nullable=False,
        server_default=text("TRUE"),
        comment="Is the reminder active",
    )

    interval_mileage: Mapped[int | None] = mapped_column(
        nullable=True,
        comment="Interval mileage",
    )

    interval_days: Mapped[int | None] = mapped_column(
        nullable=True,
        comment="Interval days",
    )

    warning_mileage: Mapped[int | None] = mapped_column(
        nullable=True,
        comment="Warning mileage",
    )

    warning_days: Mapped[int | None] = mapped_column(
        nullable=True,
        comment="Warning days",
    )

    comment: Mapped[str | None] = mapped_column(
        nullable=True,
        comment="Comment",
    )

    __table_args__ = (
        CheckConstraint(
            "(interval_mileage IS NOT NULL) OR (interval_days IS NOT NULL)",
            name="reminder_has_interval",
        ),
        Index("ix_reminders_car_active", "car_id", "is_active"),
        Index(
            "uq_reminders_active_per_item",
            "service_item_id",
            unique=True,
            postgresql_where=text("is_active = TRUE"),
        ),
    )
