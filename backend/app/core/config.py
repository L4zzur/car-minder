from enum import StrEnum
from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel, FilePath, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppMode(StrEnum):
    dev = "dev"
    prod = "prod"


class UvicornConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class ApiPrefix(BaseModel):
    prefix: str = "/api"


class AuthConfig(BaseModel):
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 1 week


class TelegramBotConfig(BaseModel):
    token: SecretStr | None = None
    webhook_secret: SecretStr | None = None

    @property
    def is_active(self) -> bool:
        return bool(self.token and self.token.get_secret_value())

    @property
    def webhook_url(self) -> str | None:
        if not self.is_active or not settings.domain:
            return None
        return f"https://{settings.domain}{settings.api.prefix}/telegram/webhook"


class CorsConfig(BaseModel):
    origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


class DatabaseConfig(BaseModel):
    file_path: FilePath
    echo: bool = False
    echo_pool: bool = False

    naming_conventions: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    @property
    def url(self) -> str:
        return f"sqlite+aiosqlite:///{self.file_path}"

    @property
    def sync_url(self) -> str:
        return f"sqlite:///{self.file_path}"

    @field_validator("file_path", mode="before")
    @classmethod
    def ensure_sqlite_file(cls, v):
        p = Path(v)
        if not p.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
            p.touch()
        elif not p.is_file():
            raise ValueError(f"{p} is not a file")
        return p


class Settings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP__",
    )
    mode: AppMode = AppMode.prod
    run: UvicornConfig = UvicornConfig()
    api: ApiPrefix = ApiPrefix()
    cors: CorsConfig = CorsConfig()
    auth: AuthConfig
    db: DatabaseConfig
    bot: TelegramBotConfig
    domain: str | None = None


settings = Settings()
