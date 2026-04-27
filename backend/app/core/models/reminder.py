from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import CreatedAtMixin, IdMixin, UpdatedAtMixin

if TYPE_CHECKING:
    from .service_item import ServiceItem


class Reminder(Base, IdMixin, CreatedAtMixin, UpdatedAtMixin):
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

    interval_km: Mapped[int | None] = mapped_column(
        nullable=True,
        comment="Service interval in kilometers",
    )

    interval_days: Mapped[int | None] = mapped_column(
        nullable=True,
        comment="Interval between services in days",
    )

    notify_before_km: Mapped[int | None] = mapped_column(
        nullable=True,
        comment="Notify this many kilometers before service is due",
    )

    notify_before_days: Mapped[int | None] = mapped_column(
        nullable=True,
        comment="Notify this many days before service is due",
    )

    note: Mapped[str | None] = mapped_column(
        nullable=True,
        comment="Additional comment or notes",
    )

    # Reminder values stay data-only; due/overdue logic should live in services/queries
    __table_args__ = (
        CheckConstraint(
            "(interval_km IS NOT NULL) OR (interval_days IS NOT NULL)",
            name="reminder_has_interval",
        ),
        CheckConstraint(
            "interval_km IS NULL OR interval_km > 0",
            name="reminder_positive_km_interval",
        ),
        CheckConstraint(
            "interval_days IS NULL OR interval_days > 0",
            name="reminder_positive_days_interval",
        ),
        CheckConstraint(
            "notify_before_km IS NULL OR notify_before_km >= 0",
            name="reminder_non_negative_km_notification_threshold",
        ),
        CheckConstraint(
            "notify_before_days IS NULL OR notify_before_days >= 0",
            name="reminder_non_negative_days_notification_threshold",
        ),
        CheckConstraint(
            "interval_km IS NULL OR notify_before_km IS NULL OR notify_before_km <= interval_km",
            name="reminder_km_notification_threshold_within_interval",
        ),
        CheckConstraint(
            "interval_days IS NULL OR notify_before_days IS NULL OR notify_before_days <= interval_days",
            name="reminder_days_notification_threshold_within_interval",
        ),
        CheckConstraint(
            "notify_before_km IS NULL OR interval_km IS NOT NULL",
            name="reminder_km_notification_requires_interval",
        ),
        CheckConstraint(
            "notify_before_days IS NULL OR interval_days IS NOT NULL",
            name="reminder_days_notification_requires_interval",
        ),
    )
