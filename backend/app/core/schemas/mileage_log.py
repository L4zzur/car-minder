from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from .base import ORMReadSchema


class MileageLogCreate(BaseModel):
    car_id: UUID
    odometer_km: int = Field(..., ge=0)


class MileageLogUpdate(BaseModel):
    odometer_km: int | None = Field(None, ge=0)


class MileageLogRead(ORMReadSchema):
    id: UUID
    car_id: UUID
    odometer_km: int
    created_at: datetime
    updated_at: datetime
