from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from .base import ORMReadSchema


class ServiceItemCreate(BaseModel):
    car_id: UUID
    name: str = Field(..., min_length=1, max_length=100)
    last_service_at: datetime
    last_service_odometer_km: int = Field(..., ge=0)


class ServiceItemUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    last_service_at: datetime | None = None
    last_service_odometer_km: int | None = Field(None, ge=0)


class ServiceItemRead(ORMReadSchema):
    id: UUID
    car_id: UUID
    name: str
    last_service_at: datetime
    last_service_odometer_km: int
    created_at: datetime
    updated_at: datetime
