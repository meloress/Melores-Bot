import re
from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Kerakli fayllar (o'zingizdagi yo'llar bo'yicha)
from database.queries import select_user  # O'zingizdagi DB funksiya
from states.registration import RegisterState

router = Router()

# --- YORDAMCHI O'ZGARUVCHILAR ---

# Viloyatlar ro'yxati va ularga mos kodlar
REGIONS = {
    "toshkent_sh": "Toshkent shahri",
    "toshkent_vil": "Toshkent viloyati",
    "andijon": "Andijon viloyati",
    "fargona": "Farg'ona viloyati",
    "namangan": "Namangan viloyati",
    "sirdaryo": "Sirdaryo viloyati",
    "jizzax": "Jizzax viloyati", # Emojini o'zgartirishingiz mumkin
    "samarqand": "Samarqand viloyati",
    "buxoro": "Buxoro viloyati",
    "navoiy": "Navoiy viloyati",
    "qashqadaryo": "Qashqadaryo viloyati",
    "surxondaryo": "Surxondaryo viloyati",
    "xorazm": "Xorazm viloyati",
    "qoraqalpogiston": "Qoraqalpog'iston Respublikasi",
}

# --- YORDAMCHI FUNKSIYALAR ---

def get_region_keyboard():
    """Viloyatlar uchun inline tugma yasash"""
    builder = InlineKeyboardBuilder()
    for key, value in REGIONS.items():
        builder.button(text=value, callback_data=key)
    builder.adjust(2) # Tugmalarni 2 qator qilib joylash
    return builder.as_markup()

# --- HANDLERS ---

@router.message(CommandStart())
async def bot_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    # user = await select_user(user_id) # DB tekshiruvi (vaqtincha o'chiq turibdi)
    user = None # Test uchun

    if user:
        await message.answer(f"👋 Salom, <b>{user['full_name']}</b>! Xush kelibsiz.")
    else:
        text = (
            "👋 <b>Assalomu alaykum!</b>\n\n"
            "Bizning xizmatlardan foydalanish uchun ro'yxatdan o'tishingiz kerak.\n\n"
            "✍️ <b>Iltimos, ism va familiyangizni to'liq kiriting:</b>\n"
            "<i>Misol: Ali Valiyev</i>"
        )
        await message.answer(text)
        await state.set_state(RegisterState.fullname)


# 1. ISM QABUL QILISH VA TEKSHIRISH
@router.message(RegisterState.fullname)
async def get_fullname(message: Message, state: FSMContext):
    fullname = message.text

    # Validatsiya: Matn ekanligini va ichida raqam yo'qligini tekshiramiz
    if not fullname or any(char.isdigit() for char in fullname):
        await message.answer(
            "🚫 <b>Noto'g'ri format!</b>\n\n"
            "Ism va familiyada raqamlar yoki begona belgilar bo'lmasligi kerak.\n"
            "✍️ <i>Iltimos, qaytadan kiriting:</i>"
        )
        return # State o'zgarmaydi, qayta so'raydi

    # Juda qisqa ism bo'lsa
    if len(fullname.split()) < 2 or len(fullname) < 5:
        await message.answer(
            "⚠️ <b>Ism juda qisqa!</b>\n\n"
            "Iltimos, <b>Ism</b> va <b>Familiyangizni</b> to'liq yozing."
        )
        return

    # Ma'lumotni saqlaymiz
    await state.update_data(fullname=fullname.title()) # Ismni chiroyli qilib (Title) saqlash

    await message.answer(
        "✅ <b>Qabul qilindi!</b>\n\n"
        "📞 Endi telefon raqamingizni yuboring.\n"
        "Format: <b>901234567</b> yoki <b>+998901234567</b>"
    )
    await state.set_state(RegisterState.phone)


# 2. TELEFON RAQAM QABUL QILISH VA FORMATLASH
@router.message(RegisterState.phone)
async def get_phone(message: Message, state: FSMContext):
    raw_phone = message.text or ""
    
    # Faqat raqamlarni ajratib olamiz
    only_digits = re.sub(r"\D", "", raw_phone) 

    final_phone = ""

    # Logika: 
    # 1. Agar 9 ta raqam bo'lsa (901234567) -> +998 qo'shamiz
    if len(only_digits) == 9:
        final_phone = f"+998{only_digits}"
    
    # 2. Agar 12 ta raqam bo'lsa va 998 bilan boshlansa -> + qo'shamiz
    elif len(only_digits) == 12 and only_digits.startswith("998"):
        final_phone = f"+{only_digits}"
    
    # Boshqa holatlar xato hisoblanadi
    else:
        await message.answer(
            "🚫 <b>Noto'g'ri raqam formati!</b>\n\n"
            "Iltimos, O'zbekiston raqamini to'g'ri kiriting.\n"
            "Misol: <b>901234567</b>"
        )
        return

    # Regex orqali yakuniy tekshiruv (+998 va 9 ta raqam)
    if not re.match(r"^\+998\d{9}$", final_phone):
        await message.answer("🚫 Raqam O'zbekistonga tegishli emasdek tuyulyapti. Qayta urinib ko'ring.")
        return

    # Ma'lumotni saqlash
    await state.update_data(phone=final_phone)

    # Viloyat tanlash
    await message.answer(
        "✅ <b>Raqam saqlandi.</b>\n\n"
        "📍 Endi yashash hududingizni tanlang:",
        reply_markup=get_region_keyboard()
    )
    await state.set_state(RegisterState.region)


# 3. VILOYATNI TANLASH (INLINE TUGMA ORQALI)
@router.callback_query(RegisterState.region)
async def get_region(call: CallbackQuery, state: FSMContext):
    region_code = call.data
    
    # Agar callback ma'lumoti bizning ro'yxatda bo'lmasa (xavfsizlik uchun)
    if region_code not in REGIONS:
        await call.answer("🚫 Noto'g'ri hudud tanlandi!", show_alert=True)
        return

    region_name = REGIONS[region_code]
    
    # Ma'lumotni saqlash
    await state.update_data(region=region_name)
    
    # Barcha ma'lumotlarni olish
    data = await state.get_data()
    
    # --- BU YERDA BAZAGA YOZISH KODI BO'LADI ---
    # await db.add_user(fullname=data['fullname'], phone=data['phone'], region=data['region'])
    # -------------------------------------------

    # Xabarni tahrirlash (tugmalarni yo'qotish uchun)
    await call.message.edit_text(
        f"🎉 <b>Tabriklaymiz, ro'yxatdan o'tdingiz!</b>\n\n"
        f"👤 <b>Ism:</b> {data['fullname']}\n"
        f"📞 <b>Tel:</b> {data['phone']}\n"
        f"📍 <b>Hudud:</b> {region_name}\n\n"
        f"🤖 Botdan foydalanishingiz mumkin."
    )
    
    await state.clear() # State ni tugatish
    await call.answer()


# Agar foydalanuvchi tugmani bosmasdan yozib yuborsa
@router.message(RegisterState.region)
async def warning_region(message: Message):
    await message.delete() # Yozganini o'chiramiz
    await message.answer(
        "📍 <b>Iltimos, quyidagi tugmalardan birini tanlang!</b>\n"
        "Yozma xabar qabul qilinmaydi.",
        reply_markup=get_region_keyboard()
    )