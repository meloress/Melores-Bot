import asyncio
from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import db 
from database.queries import (
    get_lesson, update_user_lesson,         
    get_remont_lesson, update_user_remont,
    update_last_message_id # Yangi
)

async def send_scheduled_lessons(bot: Bot):
    print("⏰ Авто-дарслик юбориш жараёни...")

    users = await db.fetch_all("""
        SELECT telegram_id, last_lesson_id, last_remont_id, active_section, last_message_id
        FROM users 
        WHERE is_banned = FALSE AND active_section IS NOT NULL
    """)
    
    if not users:
        print("📭 Ҳозирча ҳеч ким видео кўриш жараёнида эмас.")
        return

    for user in users:
        user_id = user['telegram_id']
        section = user['active_section']     
        old_msg_id = user['last_message_id'] 
        
        target_video = None
        next_id = 0
        update_func = None

        
        if section == 'lesson':
            next_id = (user['last_lesson_id'] or 0) + 1
            target_video = await get_lesson(next_id)
            update_func = update_user_lesson

        
        elif section == 'remont':
            next_id = (user['last_remont_id'] or 0) + 1
            target_video = await get_remont_lesson(next_id) 
            update_func = update_user_remont
        
       
        if target_video:
            try:
                if old_msg_id:
                    try:
                        await bot.edit_message_reply_markup(chat_id=user_id, message_id=old_msg_id, reply_markup=None)
                    except Exception:
                        pass 
                builder = InlineKeyboardBuilder()
                callback_val = "next_lesson" if section == 'lesson' else "next_remont_lesson"
                builder.button(text="Кейингиси ➡️", callback_data=callback_val)

                caption_text = target_video['caption']

                sent_msg = await bot.send_video(
                    chat_id=user_id,
                    video=target_video['file_id'],
                    caption=caption_text,
                    reply_markup=builder.as_markup()
                )
                await update_func(user_id, next_id)
                await update_last_message_id(user_id, sent_msg.message_id)

                await asyncio.sleep(0.05) 

            except Exception as e:
                pass
    
    print("🏁 Тарқатиш тугади.")
