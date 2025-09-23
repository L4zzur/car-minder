from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.mixins import CreatedAtMixin, IdMixin, UpdatedAtMixin

from .base import Base

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

    last_service_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Date of the last service",
    )

    last_service_mileage: Mapped[int] = mapped_column(
        nullable=False,
        comment="Mileage of the last service",
    )

    __table_args__ = (
        UniqueConstraint("car_id", "name", name="uq_service_items_car_name"),
        Index("ix_service_items_car", "car_id"),
        CheckConstraint(
            "last_service_mileage >= 0", name="service_item_mileage_non_negative"
        ),
    )
