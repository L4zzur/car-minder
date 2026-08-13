from fastapi import APIRouter

from core.version import __version__

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "version": __version__,
    }
