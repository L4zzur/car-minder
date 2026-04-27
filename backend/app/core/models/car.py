from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import CreatedAtMixin, IdMixin, UpdatedAtMixin

if TYPE_CHECKING:
    from .mileage_log import MileageLog
    from .service_item import ServiceItem
    from .user import User


class Car(Base, IdMixin, CreatedAtMixin, UpdatedAtMixin):
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
        comment="Owner user ID",
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

    initial_odometer_km: Mapped[int] = mapped_column(
        nullable=False,
        comment="Odometer reading when the car was added",
    )

    mileage_logs: Mapped[list["MileageLog"]] = relationship(
        back_populates="car",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    service_items: Mapped[list["ServiceItem"]] = relationship(
        back_populates="car",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        CheckConstraint(
            "length(trim(brand)) > 0",
            name="car_brand_not_blank",
        ),
        CheckConstraint(
            "length(trim(model)) > 0",
            name="car_model_not_blank",
        ),
        CheckConstraint(
            "initial_odometer_km >= 0",
            name="car_initial_odometer_non_negative",
        ),
        CheckConstraint(
            "year >= 1930 AND year <= CAST(strftime('%Y','now') AS INTEGER)",
            name="car_year_valid",
        ),
    )
