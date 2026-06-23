from core.config import settings

ACCESS_TOKEN_COOKIE = "access_token"
CSRF_TOKEN_COOKIE = "csrf_token"


def get_cookie_secure_flag() -> bool:
    return settings.mode == "prod"
