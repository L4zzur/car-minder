from enum import Enum
from pathlib import Path

from pydantic import BaseModel, FilePath, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppMode(Enum):
    dev = 1
    prod = 2


class UvicornConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class ApiPrefix(BaseModel):
    prefix: str = "/api"


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
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP__",
    )
    app_mode: int = AppMode.dev
    run: UvicornConfig = UvicornConfig()
    api: ApiPrefix = ApiPrefix()
    db: DatabaseConfig


settings = Settings()
