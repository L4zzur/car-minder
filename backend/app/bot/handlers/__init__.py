from aiogram import Router

from .general import router as general_router
from .language import router as language_router

router = Router()

router.include_router(general_router)
router.include_router(language_router)
