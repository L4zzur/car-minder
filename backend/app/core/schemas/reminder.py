from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from .base import ORMReadSchema


class ReminderValidationData(BaseModel):
    interval_km: int | None = None
    interval_days: int | None = None
    notify_before_km: int | None = None
    notify_before_days: int | None = None


def validate_reminder_fields(data: ReminderValidationData) -> ReminderValidationData:
    """Validate reminder intervals and notification thresholds"""

    if data.interval_km is None and data.interval_days is None:
        raise ValueError(
            "At least one of 'interval_km' or 'interval_days' must be provided"
        )

    if data.notify_before_km is not None:
        if data.interval_km is None:
            raise ValueError(
                "If 'notify_before_km' is set, 'interval_km' must be provided"
            )
        if data.notify_before_km > data.interval_km:
            raise ValueError(
                "'notify_before_km' "
                f"({data.notify_before_km}) "
                "cannot be greater than 'interval_km' "
                f"({data.interval_km})"
            )

    if data.notify_before_days is not None:
        if data.interval_days is None:
            raise ValueError(
                "If 'notify_before_days' is set, 'interval_days' must be provided"
            )
        if data.notify_before_days > data.interval_days:
            raise ValueError(
                "'notify_before_days' "
                f"({data.notify_before_days}) "
                "cannot be greater than 'interval_days' "
                f"({data.interval_days})"
            )

    return data


class ReminderCreate(BaseModel):
    service_item_id: UUID
    is_active: bool = True
    interval_km: int | None = Field(None, gt=0)
    interval_days: int | None = Field(None, gt=0)
    notify_before_km: int | None = Field(None, ge=0)
    notify_before_days: int | None = Field(None, ge=0)
    note: str | None = Field(None, max_length=1000)

    @model_validator(mode="after")
    def validate_intervals_and_warnings(self) -> "ReminderCreate":
        validate_reminder_fields(
            ReminderValidationData(
                interval_km=self.interval_km,
                interval_days=self.interval_days,
                notify_before_km=self.notify_before_km,
                notify_before_days=self.notify_before_days,
            )
        )
        return self


class ReminderUpdate(BaseModel):
    is_active: bool | None = None
    interval_km: int | None = Field(None, gt=0)
    interval_days: int | None = Field(None, gt=0)
    notify_before_km: int | None = Field(None, ge=0)
    notify_before_days: int | None = Field(None, ge=0)
    note: str | None = Field(None, max_length=1000)


class ReminderRead(ORMReadSchema):
    id: UUID
    service_item_id: UUID
    is_active: bool
    interval_km: int | None
    interval_days: int | None
    notify_before_km: int | None
    notify_before_days: int | None
    note: str | None
    created_at: datetime
    updated_at: datetime
