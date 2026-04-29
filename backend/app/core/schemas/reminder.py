from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from core.validators import ReminderIntervalData, validate_reminder_intervals

from .base import ORMReadSchema


def validate_reminder_fields(data: ReminderIntervalData) -> ReminderIntervalData:
    """Validate reminder intervals and notification thresholds"""
    validate_reminder_intervals(data)
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
            ReminderIntervalData(
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
