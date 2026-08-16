from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from .base import ORMReadSchema


class UserCreate(BaseModel):
    username: str = Field(..., min_length=4, max_length=50)
    name: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8, max_length=100)
    email: EmailStr | None = None

    @field_validator("username", "name", mode="before")
    @classmethod
    def strip_whitespace(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip()
        return v


class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=4, max_length=50)
    name: str | None = Field(None, min_length=3, max_length=100)
    email: EmailStr | None = None

    @field_validator("username", "name", mode="before")
    @classmethod
    def strip_whitespace(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip()
        return v


class UserRead(ORMReadSchema):
    id: UUID
    telegram_id: int | None = None
    username: str
    name: str
    email: str | None = None
    created_at: datetime
    updated_at: datetime
