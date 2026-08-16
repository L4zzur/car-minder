import logging
import sys
from typing import ClassVar

from core.config import AppMode, settings


class CustomFormatter(logging.Formatter):
    """Custom formatter that colors ONLY the log level badge in dev mode."""

    COLOR_CODES: ClassVar[dict[int, str]] = {
        logging.DEBUG: "\x1b[38;20m",  # Grey
        logging.INFO: "\x1b[34;20m",  # Blue
        logging.WARNING: "\x1b[33;20m",  # Yellow
        logging.ERROR: "\x1b[31;20m",  # Red
        logging.CRITICAL: "\x1b[31;1m",  # Bold Red
    }
    RESET: ClassVar[str] = "\x1b[0m"

    def format(self, record: logging.LogRecord) -> str:
        orig_levelname = record.levelname
        if settings.mode == AppMode.dev:
            color = self.COLOR_CODES.get(record.levelno, self.RESET)
            # Colorize ONLY the 8-char padded level name badge
            record.levelname = f"{color}{orig_levelname:<8}{self.RESET}"
        else:
            record.levelname = f"{orig_levelname:<8}"

        result = super().format(record)
        record.levelname = orig_levelname
        return result


def setup_logging() -> None:
    is_dev = settings.mode == AppMode.dev
    app_log_level = logging.DEBUG if is_dev else logging.INFO

    if is_dev:
        fmt = "%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    else:
        fmt = "%(asctime)s | %(levelname)s | %(name)s - %(message)s"

    datefmt = "%Y-%m-%d %H:%M:%S"
    formatter = CustomFormatter(fmt=fmt, datefmt=datefmt)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Root logger at INFO to prevent external libraries from spamming DEBUG
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = [handler]

    # Intercept Uvicorn loggers
    for uvicorn_logger_name in ("uvicorn", "uvicorn.error"):
        u_logger = logging.getLogger(uvicorn_logger_name)
        u_logger.handlers = [handler]
        u_logger.propagate = False
        u_logger.setLevel(logging.INFO)

    # Disable default uvicorn.access logger in favor of custom API access middleware
    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.disabled = True

    # Mute noisy internal loggers that spam DEBUG logs
    for noisy_logger_name in ("asyncio", "aiosqlite", "sqlalchemy", "aiogram"):
        logging.getLogger(noisy_logger_name).setLevel(logging.WARNING)

    # Application logger
    app_logger = logging.getLogger("car_minder")
    app_logger.setLevel(app_log_level)


logger = logging.getLogger("car_minder")
