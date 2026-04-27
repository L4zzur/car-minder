from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import CreatedAtMixin, IdMixin

if TYPE_CHECKING:
    from .car import Car


class MileageLog(Base, IdMixin, CreatedAtMixin):
    car_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "cars.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        comment="ID of the car",
    )

    car: Mapped["Car"] = relationship(back_populates="mileage_logs")

    odometer_km: Mapped[int] = mapped_column(
        nullable=False,
        comment="Full odometer reading in kilometers",
    )

    # Supports fetching mileage history and the latest reading per car efficiently
    __table_args__ = (
        Index(
            "ix_mileage_logs_car_created_at",
            "car_id",
            "created_at",
        ),
        CheckConstraint("odometer_km >= 0", name="mileage_log_odometer_non_negative"),
    )
