from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, text
from sqlalchemy.ext import hybrid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import CreatedAtMixin, IdMixin, UpdatedAtMixin

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
        comment="Interval between services in km",
    )

    interval_days: Mapped[int | None] = mapped_column(
        nullable=True,
        comment="Interval between services in days",
    )

    warning_mileage_before: Mapped[int | None] = mapped_column(
        nullable=True,
        comment="Warn X km before service due",
    )

    warning_days_before: Mapped[int | None] = mapped_column(
        nullable=True,
        comment="Warn X days before service due",
    )

    comment: Mapped[str | None] = mapped_column(
        nullable=True,
        comment="Additional comment or notes",
    )

    @hybrid.hybrid_property
    def next_service_mileage(self) -> int | None:
        if not self.interval_mileage:
            return None
        return self.service_item.last_service_mileage + self.interval_mileage

    @hybrid.hybrid_property
    def next_service_date(self) -> datetime | None:
        if not self.interval_days:
            return None
        return self.service_item.last_service_date + timedelta(days=self.interval_days)

    @hybrid.hybrid_property
    def is_overdue(self) -> bool:
        """Is the service item overdue?"""
        now = datetime.now(timezone.utc)
        car_mileage = self.car.mileage

        # Checking for mileage
        if self.next_service_mileage and car_mileage > self.next_service_mileage:
            return True

        # Checking for date
        if self.next_service_date and now > self.next_service_date:
            return True

        return False

    @hybrid.hybrid_property
    def is_due_soon(self) -> bool:
        """Is the service item due soon?"""
        now = datetime.now(timezone.utc)
        car_mileage = self.car.mileage

        # Checking for mileage
        if (
            self.next_service_mileage
            and self.warning_mileage_before
            and car_mileage >= (self.next_service_mileage - self.warning_mileage_before)
        ):
            return True

        # Checking for date
        if self.next_service_date and self.warning_days_before:
            warning_date = self.next_service_date - timedelta(
                days=self.warning_days_before
            )
            if now >= warning_date:
                return True

        return False

    __table_args__ = (
        CheckConstraint(
            "(interval_mileage IS NOT NULL) OR (interval_days IS NOT NULL)",
            name="reminder_has_interval",
        ),
        CheckConstraint(
            "interval_mileage IS NULL OR interval_mileage > 0",
            name="reminder_positive_mileage_interval",
        ),
        CheckConstraint(
            "interval_days IS NULL OR interval_days > 0",
            name="reminder_positive_days_interval",
        ),
        CheckConstraint(
            "warning_mileage_before IS NULL OR warning_mileage_before >= 0",
            name="reminder_non_negative_mileage_warning",
        ),
        CheckConstraint(
            "warning_days_before IS NULL OR warning_days_before >= 0",
            name="reminder_non_negative_days_warning",
        ),
        Index("ix_reminders_car_active", "car_id", "is_active"),
    )
