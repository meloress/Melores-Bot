from aiogram import Router, F
from aiogram.types import Message
from database.queries import update_media, add_lesson, add_remont_lesson, add_about_lesson
from data.config import (
    MAIN_GROUP_ID, 
    TOPIC_ID_VIDEO_1, 
    TOPIC_ID_DARSLIK, 
    TOPIC_ID_REMONT, 
    TOPIC_ID_BIZ_HAQIMIZDA
)

router = Router()

# -----------------------------------------------------------
# 1. VIDEO #1 (Yumaloq video)
# -----------------------------------------------------------
@router.message(
    F.chat.id == int(MAIN_GROUP_ID), 
    F.message_thread_id == int(TOPIC_ID_VIDEO_1),
    F.text.startswith("#"), 
    F.reply_to_message.video_note
)
async def save_video_note(message: Message):
    key = message.text.split()[0] 
    file_id = message.reply_to_message.video_note.file_id
    await update_media(key=key, file_id=file_id, caption=None)
    await message.reply(f"✅ <b>Video muvaffaqiyatli saqlandi!</b>\n\n🔑 Kalit: {key}")


# -----------------------------------------------------------
# 2. YANGI UYLAR (DARSLIK)
# -----------------------------------------------------------
@router.message(
    F.chat.id == int(MAIN_GROUP_ID), 
    F.message_thread_id == int(TOPIC_ID_DARSLIK),
    F.video, 
    F.caption.startswith("#")
)
async def save_lesson_video(message: Message):
    caption_full = message.caption
    try:
        parts = caption_full.split(maxsplit=1)
        lesson_id = int(parts[0].replace("#", ""))
        description = parts[1] if len(parts) > 1 else ""
        
        await add_lesson(lesson_id=lesson_id, file_id=message.video.file_id, caption=description)
        await message.reply(f"✅ <b>Yangi uy videosi #{lesson_id} saqlandi!</b>\n📝 {description}")
    except ValueError:
        await message.reply("❌ Xatolik! Format: #1 Izoh")


# -----------------------------------------------------------
# 3. REMONT VIDEOLARI
# -----------------------------------------------------------
@router.message(
    F.chat.id == int(MAIN_GROUP_ID), 
    F.message_thread_id == int(TOPIC_ID_REMONT),
    F.video, 
    F.caption.startswith("#")
)
async def save_remont_video(message: Message):
    caption_full = message.caption
    try:
        parts = caption_full.split(maxsplit=1)
        lesson_id = int(parts[0].replace("#", ""))
        description = parts[1] if len(parts) > 1 else ""
        
        await add_remont_lesson(lesson_id=lesson_id, file_id=message.video.file_id, caption=description)
        await message.reply(f"✅ <b>Remont videosi #{lesson_id} saqlandi!</b>\n📝 {description}")
    except ValueError:
        await message.reply("❌ Xatolik! Format: #1 Izoh")


# -----------------------------------------------------------
# 4. BIZ HAQIMIZDA VIDEOLARI (YANGI)
# -----------------------------------------------------------
@router.message(
    F.chat.id == int(MAIN_GROUP_ID), 
    F.message_thread_id == int(TOPIC_ID_BIZ_HAQIMIZDA),
    F.video, 
    F.caption.startswith("#")
)
async def save_about_video(message: Message):
    caption_full = message.caption
    try:
        parts = caption_full.split(maxsplit=1)
        lesson_id = int(parts[0].replace("#", ""))
        description = parts[1] if len(parts) > 1 else ""
        
        await add_about_lesson(lesson_id=lesson_id, file_id=message.video.file_id, caption=description)
        await message.reply(f"✅ <b>Biz haqimizda videosi #{lesson_id} saqlandi!</b>\n📝 {description}")
    except ValueError:
        await message.reply("❌ Xatolik! Format: #1 Izoh")