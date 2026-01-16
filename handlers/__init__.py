from aiogram import Router
from .users import start

router = Router()

router.include_router(start.router)
