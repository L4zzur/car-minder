from aiogram import Router

from .general import router as general_router

router = Router()

router.include_router(general_router)
