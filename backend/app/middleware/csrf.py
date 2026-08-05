from fastapi import Request, status
from fastapi.responses import JSONResponse

from api.routes.auth import ACCESS_TOKEN_COOKIE, CSRF_TOKEN_COOKIE
from core.config import settings

UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
CSRF_HEADER = "x-csrf-token"
CSRF_ERROR_DETAIL = "CSRF token missing or invalid"


def is_csrf_exempt(request: Request) -> bool:
    return request.url.path == f"{settings.api.prefix}/auth/login" or (
        request.method == "POST" and request.url.path == f"{settings.api.prefix}/users"
    )


def uses_cookie_auth(request: Request) -> bool:
    return (
        not is_csrf_exempt(request)
        and request.method in UNSAFE_METHODS
        and ACCESS_TOKEN_COOKIE in request.cookies
        and "authorization" not in request.headers
    )


async def csrf_protect(request: Request, call_next):
    if uses_cookie_auth(request):
        csrf_cookie = request.cookies.get(CSRF_TOKEN_COOKIE)
        csrf_header = request.headers.get(CSRF_HEADER)
        if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": CSRF_ERROR_DETAIL},
            )

    return await call_next(request)
