from datetime import datetime, time
from typing import Literal
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .base import ORMReadSchema

Language = Literal["ru", "en"]


class UserSettingsRead(ORMReadSchema):
    id: UUID
    user_id: UUID
    service_reminder_time: time
    mileage_reminder_time: time
    mileage_prompt_interval_days: int | None = None
    timezone: str
    notify_via_telegram: bool
    notify_via_email: bool
    language: Language
    created_at: datetime
    updated_at: datetime


class UserSettingsUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    service_reminder_time: time | None = None
    mileage_reminder_time: time | None = None
    mileage_prompt_interval_days: int | None = Field(None, ge=1, le=365)
    timezone: str | None = Field(None, min_length=1, max_length=64)
    notify_via_telegram: bool | None = None
    notify_via_email: bool | None = None
    language: Language | None = None

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            ZoneInfo(v)
            return v
        except (ZoneInfoNotFoundError, ValueError):
            raise ValueError(f"Invalid IANA timezone: '{v}'") from None
