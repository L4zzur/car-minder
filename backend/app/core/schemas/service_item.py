from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .base import ORMReadSchema


class ServiceItemStatus(StrEnum):
    OK = "ok"
    SOON = "soon"
    DUE = "due"


class ServiceItemCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    car_id: UUID
    name: str = Field(..., min_length=1, max_length=100)
    last_service_at: datetime
    last_service_odometer_km: int = Field(..., ge=0)


class ServiceItemUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(None, min_length=1, max_length=100)
    last_service_at: datetime | None = None
    last_service_odometer_km: int | None = Field(None, ge=0)


class ServiceItemMarkServiced(BaseModel):
    serviced_at: datetime
    odometer_km: int = Field(..., ge=0)


class ServiceItemRead(ORMReadSchema):
    id: UUID
    car_id: UUID
    name: str
    last_service_at: datetime
    last_service_odometer_km: int
    created_at: datetime
    updated_at: datetime


class ServiceItemSummary(ServiceItemRead):
    status: ServiceItemStatus = ServiceItemStatus.OK
    km_until_due: int | None = None
    days_until_due: int | None = None
