from uuid import UUID

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: UUID | None = None


class TelegramAuthRequest(BaseModel):
    init_data_raw: str


class TelegramLinkTokenResponse(BaseModel):
    token: str
    bot_username: str | None = None
