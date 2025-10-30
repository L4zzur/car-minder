from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import CreatedAtMixin, IdMixin, UpdatedAtMixin

if TYPE_CHECKING:
    from .car import Car


class MileageLog(Base, IdMixin, CreatedAtMixin, UpdatedAtMixin):
    car_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "cars.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        comment="ID of the car",
    )

    car: Mapped["Car"] = relationship(back_populates="mileage_logs")

    mileage: Mapped[int] = mapped_column(
        nullable=False,
        comment="Mileage",
    )

    __table_args__ = (
        Index(
            "ix_mileage_logs_car_created_at_desc",
            "car_id",
            "created_at",
        ),
        CheckConstraint("mileage >= 0", name="mileage_non_negative"),
    )
