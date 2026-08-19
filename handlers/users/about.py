from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from database.queries import (
    select_user, 
    get_about_lesson, 
    update_user_about,
    update_last_message_id   
)

router = Router()

# --------------------------------------------------------
# 1. "ℹ️ Biz haqimizda" 
# --------------------------------------------------------
@router.message(F.text == "ℹ️ Биз ҳақимизда")
async def start_about(message: Message):
    user_id = message.from_user.id
    
    
    user = await select_user(user_id)
    
    if user:
        current_level = user['last_about_id']
    else:
        current_level = 0
        
    next_level = current_level + 1
    
    await send_about_to_user(message.bot, user_id, next_level)


# --------------------------------------------------------
# 2. "KEYINGISI ➡️" 
# --------------------------------------------------------
@router.callback_query(F.data == "next_about")
async def next_about_handler(call: CallbackQuery):
    user_id = call.from_user.id
    
    
    user = await select_user(user_id)
    
    current_level = user['last_about_id']
    next_level = current_level + 1
    
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await send_about_to_user(call.bot, user_id, next_level)
    await call.answer()


# --------------------------------------------------------
# 3. YUBORISH MANTIQI (Video yoki Zamer tugmasi)
# --------------------------------------------------------
async def send_about_to_user(bot, user_id, lesson_id):
    lesson = await get_about_lesson(lesson_id)
    
    # ----------------------------------------------------
    # A) VIDEO TUGASA -> ZAMERGA YO'NALTIRISH
    # ----------------------------------------------------
    if not lesson:
        builder = InlineKeyboardBuilder()
        builder.button(text="📏 Замер белгилаш", callback_data="go_to_zamer_process")
        
        final_text = (
            "🏢 <b>Мелорес билан яқиндан танишганингиздан хурсандмиз!</b>\n\n"
            "😊 Биз сизнинг мебелларингизни орзуингиздагидек қилишга тайёрмиз.\n"
            "📏 Келинг, ҳаммасини аниқ ўлчовдан бошлаймиз\n\n"
            "👇 <i>Давом этиш учун тугмани босинг:</i>"
        )

        await bot.send_message(
            chat_id=user_id,
            text=final_text,
            reply_markup=builder.as_markup()
        )
        return

    # ----------------------------------------------------
    # B) VIDEO YUBORISH
    # ----------------------------------------------------
    builder = InlineKeyboardBuilder()
    builder.button(text="🟢 Кейингиси ➡️", callback_data="next_about")
    
    try:
        sent_msg = await bot.send_video(
            chat_id=user_id,
            video=lesson['file_id'],
            caption=lesson['caption'],
            reply_markup=builder.as_markup()
        )
        
        await update_user_about(user_id, lesson_id)
        
        await update_last_message_id(user_id, sent_msg.message_id)
        
    except Exception as e:
        print(f"Видео юборишда хатолик ({user_id}): {e}")
