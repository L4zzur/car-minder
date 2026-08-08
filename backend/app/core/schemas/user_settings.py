from datetime import datetime, time
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, Field, field_validator

from .base import ORMReadSchema


class UserSettingsRead(ORMReadSchema):
    id: UUID
    user_id: UUID
    service_reminder_time: time
    mileage_reminder_time: time
    mileage_prompt_interval_days: int | None = None
    timezone: str
    notify_via_telegram: bool
    notify_via_email: bool
    language: str
    created_at: datetime
    updated_at: datetime


class UserSettingsUpdate(BaseModel):
    service_reminder_time: time | None = None
    mileage_reminder_time: time | None = None
    mileage_prompt_interval_days: int | None = Field(None, ge=1, le=365)
    timezone: str | None = Field(None, min_length=1, max_length=64)
    notify_via_telegram: bool | None = None
    notify_via_email: bool | None = None
    language: str | None = Field(None, min_length=2, max_length=10)

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            ZoneInfo(v)
            return v
        except (ZoneInfoNotFoundError, ValueError):
            raise ValueError(f"Invalid IANA timezone: '{v}'")

