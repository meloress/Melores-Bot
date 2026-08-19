from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from database.queries import (
    select_user, 
    get_remont_lesson, 
    update_user_remont,
    update_active_section,   
    update_last_message_id   
)

router = Router()

# --------------------------------------------------------
# 1. "🛠️  Ремонт кетяпти" 
# --------------------------------------------------------
@router.message(F.text.contains("Ремонт"))
async def start_remont(message: Message):
    user_id = message.from_user.id
    
    await update_active_section(user_id, "remont")

    user = await select_user(user_id)
    
    if user:
        current_level = user['last_remont_id']
    else:
        current_level = 0
        
    next_level = current_level + 1
    
    await send_remont_to_user(message.bot, user_id, next_level)


# --------------------------------------------------------
# 2. "KEYINGISI ➡️" 
# --------------------------------------------------------
@router.callback_query(F.data == "next_remont")
async def next_remont_handler(call: CallbackQuery):
    user_id = call.from_user.id
    
    await update_active_section(user_id, "remont")

    user = await select_user(user_id)
    
    current_level = user['last_remont_id']
    next_level = current_level + 1
    
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await send_remont_to_user(call.bot, user_id, next_level)
    await call.answer()


# --------------------------------------------------------
# 3. YUBORISH MANTIQI
# --------------------------------------------------------
async def send_remont_to_user(bot, user_id, lesson_id):
    lesson = await get_remont_lesson(lesson_id)
    
    # ----------------------------------------------------
    # A) AGAR VIDEO TOPILMASA (Darslar tugagan bo'lsa)
    # ----------------------------------------------------
    if not lesson:
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Ҳа, тушунарли", callback_data="all_clear")
        builder.button(text="❌ Йўқ, саволим бор", callback_data="has_question")
        builder.adjust(1)

        await bot.send_message(
            chat_id=user_id,
            text=(
                "💬 <b>Мелорес учун сизнинг тушунишингиз муҳим!</b>\n\n"
                "❓ <b>Ҳамма саволларингизга жавоб олдингизми?</b>\n"
                "Агар саволларингиз бўлса — ёзинг 👇"
            ),
            reply_markup=builder.as_markup()
        )
        return

    # ----------------------------------------------------
    # B) AGAR VIDEO BOR BO'LSA (Yuboramiz)
    # ----------------------------------------------------
    builder = InlineKeyboardBuilder()
    builder.button(text="🟢 Кейингиси ➡️", callback_data="next_remont")
    
    try:
        sent_msg = await bot.send_video(
            chat_id=user_id,
            video=lesson['file_id'],
            caption=lesson['caption'],
            reply_markup=builder.as_markup()
        )
        
        await update_user_remont(user_id, lesson_id)
        
        await update_last_message_id(user_id, sent_msg.message_id)
        
    except Exception as e:
        print(f"Видео юборишда хатолик ({user_id}): {e}")
