import re
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message, CallbackQuery, 
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove 
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.queries import select_user, add_user, get_media, check_if_admin_exists
from database.db import db
from states.registration import RegisterState
from keyboards.default.menu import main_menu 
from keyboards.default.admin_keyboards import super_admin_menu, regular_admin_menu 
from data.config import MAIN_GROUP_ID, TOPIC_ID_USERLAR, SUPER_ADMIN_ID

router = Router()

# --- VILOYATLAR RO'YXATI ---
REGIONS = {
    "toshkent_sh": "📍 Тошкент шахри",
    "toshkent_vil": "📍 Тошкент вилояти",
    "andijon": "📍 Андижон вилояти",
    "fargona": "📍 Фарғона вилояти",
    "namangan": "📍 Наманган вилояти",
    "sirdaryo": "📍 Сирдарё вилояти",
    "jizzax": "📍 Жиззах вилояти",
    "samarqand": "📍 Самарқанд вилояти",
    "buxoro": "📍 Бухоро вилояти",
    "navoiy": "📍 Навоий вилояти",
    "qashqadaryo": "📍 Қашқадарё вилояти",
    "surxondaryo": "📍 Сурхондарё вилояти",
    "xorazm": "📍 Хоразм вилояти",
    "qoraqalpogiston": "📍 Қорақалпоғистон Республикаси",
}

def get_region_keyboard():
    builder = InlineKeyboardBuilder()
    for key, value in REGIONS.items():
        builder.button(text=value, callback_data=key)
    builder.adjust(2) 
    return builder.as_markup()


@router.message(Command("reset"))
async def reset_user(message: Message):
    await db.execute("DELETE FROM users WHERE telegram_id = $1", message.from_user.id)
    await message.answer("🗑 Маълумотларингиз ўчирилди. /start босиб қайта киришингиз мумкин.")


@router.message(CommandStart())
async def bot_start(message: Message, state: FSMContext):
    user_id = message.from_user.id

    # -----------------------------------------------------------
    # 1. QOROVUL TEKSHIRUVI (ADMIN FACE CONTROL) 🔥
    # -----------------------------------------------------------
    
    if user_id == SUPER_ADMIN_ID:
        await message.answer(
            f"🕴 <b>Admin Panelga xush kelibsiz, BOSS!</b>\n\n"
            "Sizda to'liq boshqaruv huquqi mavjud.",
            reply_markup=super_admin_menu 
        )
        return

    is_db_admin = await check_if_admin_exists(user_id)
    if is_db_admin:
        await message.answer(
            f"👔 <b>Admin Panelga xush kelibsiz!</b>\n\n"
            "Ishlash uchun bo'limni tanlang 👇",
            reply_markup=regular_admin_menu 
        )
        return


    # -----------------------------------------------------------
    # 2. ODDIY FOYDALANUVCHI (USER FLOW)
    # -----------------------------------------------------------
    user = await select_user(user_id)

    if user:
        await message.answer(
            f"👋 Салом, <b>{user['full_name']}</b>! Хуш келибсиз.",
            reply_markup=main_menu
        )
    else:
        text = (
            "👋 <b>Ассалому алайкум!</b>\n\n"
            "Кўпчилик мебел буюртма қилаётганда хато қилади ва ортиқча пул тўлайди бу бот сизга <b>шу хатолардан қочиш</b> ва <b>тўғри нархни билиш</b> учун яратилган.\n\n"
            "✍️ <b>Илтимос, исм ва фамилиянгизни тўлиқ киритинг:</b>\n"
            "<i>Мисол: Али Валиев</i>"
        )
        await message.answer(text)
        await state.set_state(RegisterState.fullname)


@router.message(RegisterState.fullname)
async def get_fullname(message: Message, state: FSMContext):
    raw_fullname = message.text

    if not raw_fullname or any(char.isdigit() for char in raw_fullname):
        await message.answer("🚫 <b>Нотоғри формат!</b>\nИсмда рақам қатнашмаслиги керак. Қайта киритинг:")
        return

    if len(raw_fullname.split()) < 2 or len(raw_fullname) < 5:
        await message.answer("⚠️ <b>Исм жуда қисқа!</b>\nИлтимос, исм ва фамилиянгизни тўлиқ ёзинг.")
        return

    formatted_parts = [part.capitalize() for part in raw_fullname.split()]
    fullname = " ".join(formatted_parts)

    await state.update_data(fullname=fullname)

    contact_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📞 Телефон рақамни юбориш", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer(
        "✅ <b>Қабул қилинди!</b>\n\n"
        "📞 <b>Энди телефон рақамингизни киритинг.</b>\n\n"
        "Пастдаги тугмани босинг ёки рақамни қўлда ёзинг:\n"
        "Формат: <code>901234567</code>",
        reply_markup=contact_keyboard
    )
    await state.set_state(RegisterState.phone)


@router.message(RegisterState.phone)
async def get_phone(message: Message, state: FSMContext):
    final_phone = ""
    
    if message.contact:
        final_phone = message.contact.phone_number
        if not final_phone.startswith("+"):
            final_phone = f"+{final_phone}"
    else:
        raw_phone = message.text or ""
        only_digits = re.sub(r"\D", "", raw_phone)

        if len(only_digits) == 9:
            final_phone = f"+998{only_digits}"
        elif len(only_digits) == 12 and only_digits.startswith("998"):
            final_phone = f"+{only_digits}"
        else:
            await message.answer("🚫 <b>Нотоғри формат!</b>\nИлтимос, тугмани босинг ёки рақамни 901234567 шаклида ёзинг.")
            return

    if not final_phone.startswith("+998"):
         await message.answer("🚫 Фақат <b>Ўзбекистон</b> рақамлари қабул қилинади (+998).")
         return

    await state.update_data(phone=final_phone)

    loader_msg = await message.answer("⏳", reply_markup=ReplyKeyboardRemove())
    await loader_msg.delete() 

    await message.answer(
        "✅ <b>Рақам сақланди.</b>\n\n"
        "📍 <b>Яшаш ҳудудингизни танланг:</b>",
        reply_markup=get_region_keyboard()
    )
    await state.set_state(RegisterState.region)


@router.callback_query(RegisterState.region)
async def get_region(call: CallbackQuery, state: FSMContext):
    region_code = call.data
    region_name = REGIONS[region_code]
    
    await state.update_data(region=region_name)
    data = await state.get_data()
    
    username = call.from_user.username

    await add_user(
        telegram_id=call.from_user.id,
        full_name=data['fullname'],
        username=username,
        phone=data['phone'],
        region=data['region']
    )
    
    await call.message.delete()

    try:
        if username:
            user_link = f"@{username}" 
        else:
            user_link = f"<a href='tg://user?id={call.from_user.id}'>{data['fullname']}</a>"

        admin_msg = (
            f"📣 <b>Yangi foydalanuvchi ro'yxatdan o'tdi!</b>\n\n"
            f"👤 <b>Ism:</b> {data['fullname']}\n"
            f"🔗 <b>Link:</b> {user_link}\n"
            f"🆔 <b>ID:</b> <code>{call.from_user.id}</code>\n"
            f"📞 <b>Tel:</b> {data['phone']}\n"
            f"📍 <b>Hudud:</b> {region_name}\n\n"
            f"🚀 #new_user"
        )
        
        if MAIN_GROUP_ID and TOPIC_ID_USERLAR:
            await call.bot.send_message(
                chat_id=MAIN_GROUP_ID,
                message_thread_id=TOPIC_ID_USERLAR,
                text=admin_msg
            )
            
    except Exception as e:
        print(f"Guruhga yuborishda xatolik: {e}")

    await call.message.answer(
        f"🎉 <b>Табриклаймиз, рўйхатдан ўтдингиз!</b>\n\n"
        f"👤 <b>Исм:</b> {data['fullname']}\n"
        f"📞 <b>Тел:</b> {data['phone']}\n"
        f"📍 <b>Ҳудуд:</b> {region_name}\n\n"
        f"✅ Сизнинг маълумотларингиз қабул қилинди."
    )

    media_data = await get_media(key="#1")
    
    if media_data:
        try:
            await call.message.answer_video_note(video_note=media_data['file_id'])
        except Exception:
            pass

    await call.message.answer(
        "👇 Қуйидаги менюдан фойдаланинг:",
        reply_markup=main_menu
    )
    
    await state.clear()
    await call.answer()