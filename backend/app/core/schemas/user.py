from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .base import ORMReadSchema


class UserCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    username: str = Field(..., min_length=4, max_length=50)
    name: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8, max_length=100)
    email: EmailStr | None = None


class UserUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    username: str | None = Field(None, min_length=4, max_length=50)
    name: str | None = Field(None, min_length=3, max_length=100)
    email: EmailStr | None = None


class UserRead(ORMReadSchema):
    id: UUID
    telegram_id: int | None = None
    username: str
    name: str
    email: str | None = None
    created_at: datetime
    updated_at: datetime
