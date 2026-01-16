from aiogram import Router
from .users import start, register

router = Router()

router.include_router(start.router)
router.include_router(register.router)