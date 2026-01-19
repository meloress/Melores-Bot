from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Kerakli importlar
from data.config import SUPER_ADMIN_ID

# Boshqa fayllardagi tayyor funksiyalarni chaqiramiz
# (Bu funksiyalar oldingi qadamlarda yozilgan fayllarda bo'lishi shart)
from handlers.admin.admins_management import show_admin_list
from handlers.admin.mailing import show_mailing_menu

router = Router()

# ==========================================================
# 2. 👥 FOYDALANUVCHILAR (CRM)
# ==========================================================
@router.message(F.text == "👥 Foydalanuvchilar (CRM)")
async def crm_section(message: Message):
    text = (
        "📇 <b>MIJOZLAR BAZASI (CRM)</b>\n\n"
        "Bu bo'limda siz har bir foydalanuvchi haqida shaxsiy ma'lumot olishingiz mumkin.\n\n"
        "🔍 <b>Qidiruv tartibi:</b>\n"
        "Pastdagi tugmani bosib, mijozning <b>ID raqamini</b>, <b>Username</b>ni yoki <b>Telefon raqamini</b> yuboring."
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🔎 ID orqali izlash", callback_data="crm_search_id")
    builder.button(text="🔎 Username orqali", callback_data="crm_search_username")
    builder.button(text="📞 Tel orqali izlash", callback_data="crm_search_phone")
    builder.button(text="⭐️ VIP mijozlar", callback_data="crm_filter_vip")
    builder.adjust(2)

    await message.answer(text, reply_markup=builder.as_markup())


# ==========================================================
# 3. 📨 XABAR YUBORISH (MAILING)
# ==========================================================
@router.message(F.text == "📨 Xabar yuborish")
async def mailing_section(message: Message):
    # Biz mailing.py da yozgan tayyor menyu funksiyasini chaqiramiz.
    # Bu kod takrorlanishini oldini oladi va callbacklar to'g'ri ishlashini ta'minlaydi.
    await show_mailing_menu(message)


# ==========================================================
# 4. 👮‍♂️ ADMINLAR BOSHQARUVI (FAQAT SUPER ADMIN)
# ==========================================================
@router.message(F.text == "👮‍♂️ Adminlar boshqaruvi")
async def admin_management_section(message: Message):
    # 1. XAVFSIZLIK: Faqat Super Admin kira oladi
    if message.from_user.id != SUPER_ADMIN_ID:
        await message.answer("⛔️ <b>Sizda bu bo'limga kirish huquqi yo'q.</b>")
        return

    # 2. Agar Super Admin bo'lsa, admins_management.py dagi ro'yxatni chaqiramiz
    await show_admin_list(message)


# ==========================================================
# 5. UNIVERSAL "ORQAGA" TUGMASI (Inline xabarni o'chirish)
# ==========================================================
@router.callback_query(F.data.endswith("_back"))
async def go_back_handler(call: CallbackQuery):
    await call.message.delete()
    # Asosiy Reply menyu pastda turibdi, shunchaki xabar beramiz
    await call.message.answer("🏠 <b>Asosiy menyu:</b>", reply_markup=None)