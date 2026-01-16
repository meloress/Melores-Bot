from aiogram.filters import BaseFilter
from aiogram.types import Message
from database.requests import is_admin_db
from data.config import ADMINS

class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        # .env dagi asosiy admin yoki bazadagi admin ekanligini tekshiradi
        if message.from_user.id in ADMINS:
            return True
        return await is_admin_db(message.from_user.id)