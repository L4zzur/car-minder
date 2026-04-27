from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import CreatedAtMixin, IdMixin, UpdatedAtMixin

if TYPE_CHECKING:
    from .car import Car
    from .reminder import Reminder


class ServiceItem(Base, IdMixin, CreatedAtMixin, UpdatedAtMixin):
    car_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "cars.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        comment="ID of the car",
    )

    car: Mapped["Car"] = relationship(back_populates="service_items")

    reminders: Mapped[list["Reminder"]] = relationship(
        back_populates="service_item",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    name: Mapped[str] = mapped_column(
        nullable=False,
        comment="Name of the service item",
    )

    last_service_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Date of the last service",
    )

    last_service_odometer_km: Mapped[int] = mapped_column(
        nullable=False,
        comment="Odometer reading at the last service",
    )

    # Names are unique only within a single car, not globally
    __table_args__ = (
        UniqueConstraint("car_id", "name", name="uq_service_items_car_name"),
        CheckConstraint("length(trim(name)) > 0", name="service_item_name_not_blank"),
        CheckConstraint(
            "last_service_odometer_km >= 0",
            name="service_item_odometer_non_negative",
        ),
    )
