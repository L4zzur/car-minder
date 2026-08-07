from datetime import datetime, time
from uuid import UUID

from pydantic import BaseModel, Field

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
