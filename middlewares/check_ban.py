from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from database.queries import select_user
from data.config import SUPER_ADMIN_ID

class BanCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        if not user_id:
            return await handler(event, data)

        if user_id == SUPER_ADMIN_ID:
            return await handler(event, data)

        user = await select_user(user_id)
        
        if user and user.get('is_banned'):
            text = (
                "🚫 <b>Сизнинг ҳисобингиз вақтинча блокланди.</b>\n\n"
                "⚠️ <i>Бот қоидаларини бузганлик ёки спам туфайли админ томонидан чеклов қўйилган.</i>\n\n"
                "Ҳозирча ҳеч қандай буйруқдан фойдалана олмайсиз."
            )
            
            if isinstance(event, Message):
                await event.answer(text)
            
            elif isinstance(event, CallbackQuery):
                await event.answer("🚫 Сиз блоклангисиз! Ботдан фойдалана олмайсиз.", show_alert=True)
            
            return 

        return await handler(event, data)