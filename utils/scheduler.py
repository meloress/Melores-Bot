import asyncio
from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Bazadan kerakli funksiyalarni chaqiramiz
# Agar sizda 'db' obyekti queries.py da bo'lmasa, database.db dan oling
from database.db import db 
from database.queries import (
    get_lesson, update_user_lesson,         # Yangi uy uchun
    get_remont_lesson, update_user_remont   # Remont uchun
)

async def send_scheduled_lessons(bot: Bot):
    print("⏰ Авто-дарслик юбориш бошланди...")

    # 1. Barcha aktiv (ban olmagan) userlarni olamiz
    # Bizga ularning oxirgi ko'rgan dars ID lari kerak
    users = await db.fetch_all("""
        SELECT telegram_id, last_lesson_id, last_remont_id 
        FROM users 
        WHERE is_banned = FALSE
    """)
    
    if not users:
        print("📭 Юбориш учун фойдаланувчилар йўқ.")
        return

    sent_count = 0

    for user in users:
        user_id = user['telegram_id']
        
        # ==========================================
        # 1-YO'NALISH: YANGI UYLAR (Lessons)
        # ==========================================
        last_lesson = user['last_lesson_id'] or 0
        next_lesson_id = last_lesson + 1
        
        # Bazadan keyingi darsni qidiramiz
        lesson = await get_lesson(next_lesson_id)
        
        if lesson:
            try:
                # Tugma (Kirillcha)
                builder = InlineKeyboardBuilder()
                builder.button(text="Кейингиси ➡️", callback_data="next_lesson") # Kirillcha

                caption_text = f"<b>#{lesson['id']} - Видеодарс (🏠 Янги уй)</b>\n\n{lesson['caption']}"

                await bot.send_video(
                    chat_id=user_id,
                    video=lesson['file_id'],
                    caption=caption_text,
                    reply_markup=builder.as_markup()
                )
                
                # Bazani yangilaymiz (User 8-ni ko'rdi deb yozamiz)
                await update_user_lesson(user_id, next_lesson_id)
                sent_count += 1
                await asyncio.sleep(0.05) # Spamdan saqlanish

            except Exception as e:
                # Agar user bloklagan bo'lsa
                pass

        # ==========================================
        # 2-YO'NALISH: REMONT (Remont Lessons)
        # ==========================================
        last_remont = user['last_remont_id'] or 0
        next_remont_id = last_remont + 1
        
        remont_lesson = await get_remont_lesson(next_remont_id)
        
        if remont_lesson:
            try:
                # Tugma (Kirillcha)
                builder_rem = InlineKeyboardBuilder()
                builder_rem.button(text="Кейингиси ➡️", callback_data="next_remont_lesson")

                caption_rem = f"<b>#{remont_lesson['id']} - Видеодарс (🛠 Ремонт)</b>\n\n{remont_lesson['caption']}"

                await bot.send_video(
                    chat_id=user_id,
                    video=remont_lesson['file_id'],
                    caption=caption_rem,
                    reply_markup=builder_rem.as_markup()
                )
                
                # Bazani yangilaymiz
                await update_user_remont(user_id, next_remont_id)
                sent_count += 1
                await asyncio.sleep(0.05)

            except Exception:
                pass
    
    print(f"🏁 Авто-дарслик тарқатиш тугади. Жами {sent_count} та хабар юборилди.")
