from aiogram import Bot
from database.queries import get_all_users, get_lesson, update_user_lesson
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

async def send_scheduled_lessons(bot: Bot):
    print("⏰ Avto-darslik yuborish boshlandi...")
    users = await get_all_users()
    
    for user in users:
        user_id = user['telegram_id']
        last_lesson = user['last_lesson_id']
        next_lesson = last_lesson + 1
        
        lesson = await get_lesson(next_lesson)
        
        if lesson:
            try:
                builder = InlineKeyboardBuilder()
                builder.button(text="Keyingisi ➡️", callback_data="next_lesson")

                await bot.send_video(
                    chat_id=user_id,
                    video=lesson['file_id'],
                    caption=f"<b>#{lesson['id']} - Video (Kunlik)</b>\n\n{lesson['caption']}",
                    reply_markup=builder.as_markup()
                )
                
                await update_user_lesson(user_id, next_lesson)
                
                await asyncio.sleep(0.5) 
                
            except Exception as e:
                print(f"User {user_id} ga yuborib bo'lmadi: {e}")
    
    print("🏁 Avto-darslik tarqatish tugadi.")