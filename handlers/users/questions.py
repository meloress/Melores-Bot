from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.queries import select_user
from states.registration import QuestionState
from keyboards.default.menu import main_menu
from data.config import MAIN_GROUP_ID, TOPIC_ID_ALOQA 

router = Router()

# ---------------------------------------------------------
# 1. "HA, TUSHUNARLI" -> MENUGA QAYTISH
# ---------------------------------------------------------
@router.callback_query(F.data == "all_clear")
async def all_clear_handler(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer(
        "😊 <b>Хурсандмиз!</b>\n\n"
        "Биз билан қолганингиз учун раҳмат. Керакли бўлимни менюдан танлашингиз мумкин 👇",
        reply_markup=main_menu
    )
    await call.answer()


# ---------------------------------------------------------
# 2. "SAVOLIM BOR" -> SAVOL KUTISH
# ---------------------------------------------------------
@router.callback_query(F.data == "has_question")
async def ask_question_handler(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "📝 <b>Саволингизни ёзиб қолдиринг.</b>\n\n"
        "Матн кўринишида ёзишингиз ёки овозли хабар (voice) юборишингиз мумкин.\n\n"
        "👇 <i>Марҳамат:</i>"
    )
    await state.set_state(QuestionState.waiting_question)
    await call.answer()


# ---------------------------------------------------------
# 3. SAVOLNI QABUL QILISH VA TASDIQLASHGA OLIB O'TISH
# ---------------------------------------------------------
@router.message(QuestionState.waiting_question)
async def receive_question(message: Message, state: FSMContext):
    if message.voice:
        await state.update_data(question_type="voice", question_content=message.voice.file_id)
        msg_text = "🎤 <i>(Ovozli xabar)</i>"
    elif message.text:
        await state.update_data(question_type="text", question_content=message.text)
        msg_text = message.text
    else:
        await message.answer("⚠️ Илтимос, фақат матн ёки овозли хабар юборинг.")
        return

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Тасдиқлаш (Юбориш)", callback_data="confirm_question")
    builder.button(text="✏️ Таҳрирлаш", callback_data="edit_question")
    builder.adjust(1)

    await message.answer(
        f"📝 <b>Сизнинг саволингиз:</b>\n\n"
        f"{msg_text}\n\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"Агар ҳаммаси тўғри бўлса, <b>Тасдиқлаш</b> тугмасини босинг.\n"
        f"Ўзгартириш учун <b>Таҳрирлаш</b> ни танланг.",
        reply_markup=builder.as_markup()
    )


# ---------------------------------------------------------
# 4. TAHRIRLASH (QAYTA YOZISH)
# ---------------------------------------------------------
@router.callback_query(F.data == "edit_question")
async def edit_question_handler(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "🔄 <b>Тушунарли, саволни қайтадан ёзинг:</b>\n\n"
        "👇 Марҳамат:"
    )
    await state.set_state(QuestionState.waiting_question)
    await call.answer()


# ---------------------------------------------------------
# 5. TASDIQLASH VA ADMINGA YUBORISH
# ---------------------------------------------------------
@router.callback_query(F.data == "confirm_question")
async def send_to_admin(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    q_type = data.get("question_type")
    q_content = data.get("question_content")

    user_id = call.from_user.id
    user_data = await select_user(user_id)

    if not user_data:
        full_name = call.from_user.full_name
        phone = "Noma'lum"
        region = "Noma'lum"
    else:
        full_name = user_data['full_name']
        phone = user_data['phone']
        region = user_data['region']

    if call.from_user.username:
        user_link = f"@{call.from_user.username}"
    else:
        user_link = f"<a href='tg://user?id={user_id}'>{full_name}</a>"

    admin_caption = (
        f"🆕 <b>YANGI SAVOL KELDI</b>\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"👤 <b>Ism:</b> {full_name}\n"
        f"🔗 <b>Link:</b> {user_link}\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
        f"📞 <b>Tel:</b> {phone}\n"
        f"📍 <b>Hudud:</b> {region}\n"
        f"➖➖➖➖➖➖➖➖➖➖"
    )

    try:
        if q_type == "voice":
            await call.bot.send_voice(
                chat_id=MAIN_GROUP_ID,
                message_thread_id=TOPIC_ID_ALOQA, 
                voice=q_content,
                caption=f"{admin_caption}\n🎤 <b>Format:</b> Ovozli xabar"
            )
        
        elif q_type == "text":
            full_msg = f"{admin_caption}\n📝 <b>Savol matni:</b>\n\n{q_content}"
            await call.bot.send_message(
                chat_id=MAIN_GROUP_ID,
                message_thread_id=TOPIC_ID_ALOQA,
                text=full_msg
            )

        await call.message.delete()
        await call.message.answer(
            "✅ <b>Қабул қилинди!</b>\n\n"
            "Саволингиз админларга муваффақиятли юборилди. "
            "Тез орада жавоб берамиз. 😊",
            reply_markup=main_menu
        )

    except Exception as e:
        print(f"Админга юборишда хатолик: {e}")
        await call.message.answer("⚠️ Техник хатолик, кейинроқ уриниб кўринг.", reply_markup=main_menu)

    await state.clear()
    await call.answer()