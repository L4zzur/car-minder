from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .base import ORMReadSchema


class CarCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    brand: str = Field(..., min_length=1, max_length=30)
    model: str = Field(..., min_length=1, max_length=50)
    year: int = Field(..., ge=1900)
    initial_odometer_km: int = Field(..., ge=0)

    @field_validator("year")
    @classmethod
    def validate_year(cls, v: int) -> int:
        current_year = datetime.now().year
        if v > current_year:
            raise ValueError(f"Year cannot be greater than {current_year}")
        return v


class CarUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    brand: str | None = Field(None, min_length=1, max_length=30)
    model: str | None = Field(None, min_length=1, max_length=50)
    year: int | None = Field(None, ge=1900, le=datetime.now().year)

    @field_validator("year")
    @classmethod
    def validate_year(cls, v: int | None) -> int | None:
        if v is None:
            return v
        current_year = datetime.now().year
        if v > current_year:
            raise ValueError(f"Year cannot be greater than {current_year}")
        return v


class CarRead(ORMReadSchema):
    id: UUID
    user_id: UUID
    brand: str
    model: str
    year: int
    initial_odometer_km: int
    current_odometer_km: int
    created_at: datetime
    updated_at: datetime
