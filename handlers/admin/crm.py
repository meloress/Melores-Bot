import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from database.queries import (
    select_user, get_user_by_phone, update_ban_status, 
    get_lessons_count, get_vip_users, get_user_by_username
)
from states.registration import AdminCrmState
from data.config import SUPER_ADMIN_ID

router = Router()

# ==========================================================
# 1. QIDIRUV TUGMALARI (TRIGGERS)
# ==========================================================

@router.callback_query(F.data == "crm_search_id")
async def ask_search_id(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("🔍 <b>Foydalanuvchi ID raqamini kiriting:</b>\n\n<i>Misol: 123456789</i>")
    await state.set_state(AdminCrmState.search_id)

@router.callback_query(F.data == "crm_search_phone")
async def ask_search_phone(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("📞 <b>Telefon raqamini kiriting:</b>\n\n<i>Misol: 901234567 yoki +99890...</i>")
    await state.set_state(AdminCrmState.search_phone)

@router.callback_query(F.data == "crm_search_username")
async def ask_search_username(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("👤 <b>Foydalanuvchi Username sini kiriting:</b>\n\n<i>Misol: @ali_valiyev yoki shunchaki ali_valiyev</i>")
    await state.set_state(AdminCrmState.search_username)


# ==========================================================
# 2. QIDIRUV NATIJASI VA MANTIQI
# ==========================================================

# A) ID bo'yicha qidirganda
@router.message(AdminCrmState.search_id)
async def result_by_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("⚠️ Faqat raqam kiriting!")
        return
    
    user_id = int(message.text)
    await show_user_profile(message, user_id, state)

# B) Telefon bo'yicha qidirganda
@router.message(AdminCrmState.search_phone)
async def result_by_phone(message: Message, state: FSMContext):
    phone_input = message.text
    clean_phone = re.sub(r"\D", "", phone_input) 
    
    user = await get_user_by_phone(clean_phone)
    
    if user:
        await show_user_profile(message, user['telegram_id'], state)
    else:
        await message.answer("❌ <b>Bunday raqamli foydalanuvchi topilmadi.</b>\nQaytadan urinib ko'ring yoki /cancel bosing.")

# C) Username bo'yicha qidirganda
@router.message(AdminCrmState.search_username)
async def result_by_username(message: Message, state: FSMContext):
    username_input = message.text
    
    user = await get_user_by_username(username_input)
    
    if user:
        await show_user_profile(message, user['telegram_id'], state)
    else:
        await message.answer("❌ <b>Bunday username topilmadi!</b>\n\nEslatma: User botga start bosgan paytda username'i bo'lmagan bo'lishi mumkin.\n\nQaytadan urinib ko'ring yoki /cancel bosing.")


# ----------------------------------------------------------
# 🔥 UNIVERSAL PROFIL KO'RSATISH FUNKSIYASI
# ----------------------------------------------------------
async def show_user_profile(message_or_call, user_id, state: FSMContext):
    user = await select_user(user_id)
    
    if isinstance(message_or_call, CallbackQuery):
        msg_obj = message_or_call.message
        await message_or_call.message.delete()
    else:
        msg_obj = message_or_call

    if not user:
        await msg_obj.answer("❌ <b>Foydalanuvchi topilmadi!</b>")
        return

    counts = await get_lessons_count()
    
    def calc_percent(curr, total):
        if total == 0: return 0
        p = int((curr / total) * 100)
        return 100 if p > 100 else p

    p_lesson = calc_percent(user['last_lesson_id'], counts['lessons'])
    p_remont = calc_percent(user['last_remont_id'], counts['remont'])
    p_about = calc_percent(user['last_about_id'], counts['about'])
    
    is_zamer = "✅ HA" if user['zamer_requested'] else "❌ YO'Q"
    is_banned = "🚫 BAN BERILGAN" if user.get('is_banned') else "✅ AKTIV"
    reg_date = str(user['created_at'])[:10]

    link = f"<a href='tg://user?id={user['telegram_id']}'>{user['full_name']}</a>"
    tg_username = f"@{user['username']}" if user['username'] else "❌ Mavjud emas"

    text = (
        f"👤 <b>MIJOZ PROFILI</b>\n\n"
        f"📛 <b>Ism:</b> {link}\n"
        f"🔗 <b>Username:</b> {tg_username}\n"
        f"🆔 <b>ID:</b> <code>{user['telegram_id']}</code>\n"
        f"📞 <b>Tel:</b> {user['phone']}\n"
        f"📍 <b>Hudud:</b> {user['region']}\n"
        f"📅 <b>Qo'shilgan:</b> {reg_date}\n\n"
        f"🎯 <b>Hozirgi holati:</b>\n"
        f"• 🏠 Yangi uylar: <b>{p_lesson}%</b> ({user['last_lesson_id']})\n"
        f"• 🏚 Remont: <b>{p_remont}%</b> ({user['last_remont_id']})\n"
        f"• 📏 Zamerga yozilganmi: <b>{is_zamer}</b>\n"
        f"• 🤖 Botdagi statusi: <b>{is_banned}</b>"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="📨 Xabar yozish", callback_data=f"crm_msg_{user_id}")
    
    if user.get('is_banned'):
        builder.button(text="✅ Ban dan olish", callback_data=f"crm_unban_{user_id}")
    else:
        builder.button(text="🚫 Ban berish", callback_data=f"crm_ban_{user_id}")
        
    builder.button(text="🔙 Orqaga", callback_data="crm_back_main")
    builder.adjust(2, 1)

    await msg_obj.answer(text, reply_markup=builder.as_markup())
    await state.clear()


# ==========================================================
# 3. PROFIL AMALLARI (XABAR YOZISH & BAN)
# ==========================================================

# --- BAN BERISH ---
@router.callback_query(F.data.startswith("crm_ban_"))
async def ban_user(call: CallbackQuery, state: FSMContext):
    user_id = int(call.data.split("_")[2])
    
    if user_id == SUPER_ADMIN_ID:
        await call.answer("Bossni ban qilib bo'lmaydi! 😅", show_alert=True)
        return

    await update_ban_status(user_id, True)
    await call.answer("🚫 Foydalanuvchi bloklandi!", show_alert=True)
    
    await show_user_profile(call, user_id, state)

# --- BANDAN OLISH (Xabar yuborish bilan) ---
@router.callback_query(F.data.startswith("crm_unban_"))
async def unban_user(call: CallbackQuery, state: FSMContext):
    user_id = int(call.data.split("_")[2])
    
    await update_ban_status(user_id, False)
    await call.answer("✅ Foydalanuvchi blokdan ochildi!", show_alert=True)
    
    try:
        user_msg = (
            "🎉 <b>Ажойиб янгилик!</b>\n\n"
            "Сизнинг ҳисобингиз блокдан чиқарилди. ✅\n"
            "Энди ботдан яна тўлиқ фойдаланишингиз мумкин. Марҳамат! 😊"
        )
        await call.bot.send_message(chat_id=user_id, text=user_msg)
    except Exception:
        pass

    await show_user_profile(call, user_id, state)


# --- SHAXSIY XABAR YOZISH ---
@router.callback_query(F.data.startswith("crm_msg_"))
async def start_personal_msg(call: CallbackQuery, state: FSMContext):
    user_id = int(call.data.split("_")[2])
    
    await call.message.delete()
    await call.message.answer(
        f"✍️ <b>Xabar matnini kiriting:</b>\n\n"
        f"Foydalanuvchi ID: <code>{user_id}</code>\n"
        f"<i>Rasm, video yoki matn yuborishingiz mumkin.</i>"
    )
    await state.update_data(target_id=user_id)
    await state.set_state(AdminCrmState.send_personal_msg)

@router.message(AdminCrmState.send_personal_msg)
async def send_msg_to_user(message: Message, state: FSMContext):
    data = await state.get_data()
    target_id = data.get("target_id")
    
    try:
        await message.copy_to(chat_id=target_id)
        await message.answer("✅ <b>Xabar muvaffaqiyatli yuborildi!</b>")
    except Exception as e:
        await message.answer(f"❌ <b>Yuborilmadi:</b> Foydalanuvchi botni bloklagan bo'lishi mumkin.")
    
    await show_user_profile(message, target_id, state)


# ==========================================================
# 4. VIP FILTR (ZAMER BOSGANLAR)
# ==========================================================
@router.callback_query(F.data == "crm_filter_vip")
async def show_vip_users(call: CallbackQuery):
    vips = await get_vip_users()
    
    if not vips:
        await call.answer("Hozircha Zamer so'raganlar yo'q", show_alert=True)
        return

    text = "⭐️ <b>VIP MIJOZLAR (Zamer so'raganlar - Oxirgi 10 ta):</b>\n\n"
    
    builder = InlineKeyboardBuilder()
    
    for user in vips:
        u_link = f"{user['full_name']} ({user['phone']})"
        text += f"▫️ {u_link}\n"
        builder.button(text=f"👤 {user['full_name']}", callback_data=f"crm_open_{user['telegram_id']}")
    
    builder.adjust(1)
    builder.button(text="🔙 Orqaga", callback_data="crm_back_main")
    
    await call.message.edit_text(text, reply_markup=builder.as_markup(), disable_web_page_preview=True)

@router.callback_query(F.data.startswith("crm_open_"))
async def open_from_list(call: CallbackQuery, state: FSMContext):
    user_id = int(call.data.split("_")[2])
    await show_user_profile(call, user_id, state)


# ==========================================================
# ORQAGA TUGMASI
# ==========================================================
@router.callback_query(F.data == "crm_back_main")
async def back_to_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.delete()
    await call.answer()
    await call.message.answer("👥 CRM Bo'limi yopildi. Menyudan tanlang 👇")