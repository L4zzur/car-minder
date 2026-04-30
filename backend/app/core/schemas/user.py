from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from .base import ORMReadSchema


class UserCreate(BaseModel):
    username: str = Field(..., min_length=4, max_length=50)
    name: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=4, max_length=50)
    name: str | None = Field(None, min_length=3, max_length=100)


class UserRead(ORMReadSchema):
    id: UUID
    username: str
    name: str
    created_at: datetime
    updated_at: datetime
