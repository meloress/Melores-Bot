import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

# set_zamer_flag ni ham import qildik
from database.queries import select_user, add_user, set_zamer_flag
from states.registration import ZamerState
from data.config import MAIN_GROUP_ID, TOPIC_ID_ZAMER
from keyboards.default.menu import main_menu

router = Router()

# --------------------------------------------------------
# YORDAMCHI FUNKSIYA (Mantiq shu yerda ishlaydi)
# --------------------------------------------------------
async def show_zamer_card(bot, chat_id, user_id):
    """Zamer kartasini chiqaruvchi universal funksiya"""
    user = await select_user(user_id)

    # Agar user bazada bo'lmasa
    if not user:
        await bot.send_message(chat_id, "⚠️ Илтимос, аввал /start босиб рўйхатдан ўтинг.")
        return

    # User ma'lumotlarini tayyorlaymiz
    text = (
        "👷‍♂️ <b>Замер учун аризангизни қабул қиламиз!</b>\n\n"
        "Биз сиз билан боғланишимиз учун қуйидаги маълумотлардан фойдаланамиз:\n\n"
        f"👤 <b>Исм:</b> {user['full_name']}\n"
        f"📞 <b>Тел:</b> {user['phone']}\n\n"
        "👇 <i>Маълумотлар тўғри эканлигини тасдиқланг ёки таҳрирланг:</i>"
    )

    # Tugmalar
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Тасдиқлаш (Юбориш)", callback_data="confirm_zamer")
    builder.button(text="✏️ Таҳрирлаш", callback_data="edit_zamer_start")
    builder.adjust(1)

    # Izohli matn
    info_text = (
        "\n➖➖➖➖➖➖➖➖➖➖\n"
        "✅ <b>Тасдиқлаш</b> — Аризангизни дарҳол мутахассисларга юборишади.\n"
        "✏️ <b>Таҳрирлаш</b> — Исм ёки рақамингиз ўзгарган бўлса, янгилаш имконини беради."
    )

    await bot.send_message(chat_id, text + info_text, reply_markup=builder.as_markup())


# --------------------------------------------------------
# 1. "🏚 ZAMER BELGILASH" BOSILGANDA (MENYUDAN)
# --------------------------------------------------------
@router.message(F.text == "📐 Замер белгилаш")
async def start_zamer_process(message: Message):
    # Bu yerda message.from_user.id - bu Userning o'zi
    await show_zamer_card(message.bot, message.chat.id, message.from_user.id)


# --------------------------------------------------------
# 2. "BIZ HAQIMIZDA" TUGAGANDA -> ZAMERGA O'TISH (INLINE)
# --------------------------------------------------------
@router.callback_query(F.data == "go_to_zamer_process")
async def inline_zamer_trigger(call: CallbackQuery):
    await call.message.delete()
    
    # call.from_user.id - bu tugmani bosgan User ID si.
    await show_zamer_card(call.bot, call.message.chat.id, call.from_user.id)
    
    await call.answer()


# --------------------------------------------------------
# 3. TASDIQLASH -> ADMINGA YUBORISH
# --------------------------------------------------------
@router.callback_query(F.data == "confirm_zamer")
async def submit_zamer(call: CallbackQuery):
    user_id = call.from_user.id
    user = await select_user(user_id)

    # Username yoki Link
    if call.from_user.username:
        user_link = f"@{call.from_user.username}"
    else:
        user_link = f"<a href='tg://user?id={user_id}'>{user['full_name']}</a>"

    # --- YANGI QO'SHILDI: BAZAGA ZAMER BOSDI DEB YOZISH ---
    await set_zamer_flag(user_id) 
    # ------------------------------------------------------

    # Admin shablon
    admin_msg = (
        f"📏 <b>YANGI ZAMER BUYURTMASI!</b>\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"👤 <b>Ism:</b> {user['full_name']}\n"
        f"🔗 <b>Link:</b> {user_link}\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
        f"📞 <b>Tel:</b> {user['phone']}\n"
        f"📍 <b>Hudud:</b> {user['region']}\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"🚀 #zamer #new_order"
    )

    try:
        await call.bot.send_message(
            chat_id=MAIN_GROUP_ID,
            message_thread_id=TOPIC_ID_ZAMER,
            text=admin_msg
        )
        
        await call.message.delete()
        await call.message.answer(
            "✅ <b>Аризангиз қабул қилинди!</b>\n\n"
            "Тез орада мутахассисларимиз сиз билан боғланиб, "
            "ўлчов ишларини келишиб олишади. 😊",
            reply_markup=main_menu
        )

    except Exception as e:
        print(f"Замер юборишда хатолик: {e}")
        await call.message.answer("⚠️ Хатолик юз берди. Қайта уриниб кўринг.", reply_markup=main_menu)
    
    await call.answer()


# --------------------------------------------------------
# 4. TAHRIRLASH BOSQICHI
# --------------------------------------------------------
@router.callback_query(F.data == "edit_zamer_start")
async def edit_start(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("🔄 <b>Исм Фамилиянгизни қайтадан тўлиқ киритинг:</b>")
    await state.set_state(ZamerState.fullname)
    await call.answer()

@router.message(ZamerState.fullname)
async def edit_fullname(message: Message, state: FSMContext):
    name = message.text
    if not name or len(name) < 3:
        await message.answer("⚠️ Исм жуда қисқа, тўлиқ ёзинг:")
        return
    
    await state.update_data(fullname=name)
    
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Телефон рақамни юбориш", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )
    
    await message.answer(
        "✅ <b>Исм Фамилия ўзгарди.</b>\n\n"
        "📞 Энди телефон рақамингизни юборинг ёки ёзинг:",
        reply_markup=kb
    )
    await state.set_state(ZamerState.phone)

@router.message(ZamerState.phone)
async def edit_phone(message: Message, state: FSMContext):
    final_phone = ""
    if message.contact:
        final_phone = message.contact.phone_number
        if not final_phone.startswith("+"): final_phone = f"+{final_phone}"
    else:
        raw = message.text
        nums = re.sub(r"\D", "", raw)
        if len(nums) == 9: final_phone = f"+998{nums}"
        elif len(nums) == 12: final_phone = f"+{nums}"
        else:
            await message.answer("🚫 Нотоғри рақам! Қайта киритинг:")
            return

    data = await state.get_data()
    new_name = data.get("fullname")
    user = await select_user(message.from_user.id)
    region = user['region'] if user else "Noma'lum"

    # --- USERNAME OLISH (XATOLIK SHU YERDA EDI) ---
    username = message.from_user.username

    # Bazani yangilash
    await add_user(
        telegram_id=message.from_user.id,
        full_name=new_name,
        username=username, # <--- MANA SHU QATOR QO'SHILDI
        phone=final_phone,
        region=region
    )
    
    loader = await message.answer("🔄 Маълумотлар янгиланмоқда...", reply_markup=ReplyKeyboardRemove())
    await loader.delete()

    await state.clear()

    # Yana zamer kartasini chiqaramiz (Yangilangan holda)
    await show_zamer_card(message.bot, message.chat.id, message.from_user.id)