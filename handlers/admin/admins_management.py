from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from database.queries import (
    get_all_admins_list, add_admin, delete_admin, 
    select_user
)
from states.registration import AdminManageState
from data.config import SUPER_ADMIN_ID

router = Router()

# ==========================================================
# 1. ADMINLAR RO'YXATI (Log tugmasiz)
# ==========================================================
async def show_admin_list(message_or_call):
    # Xavfsizlik: Agar bu funksiyani Super Admin bo'lmagan odam chaqirsa, ishlamasin
    user_id = message_or_call.from_user.id
    if user_id != SUPER_ADMIN_ID:
        if isinstance(message_or_call, Message):
            await message_or_call.answer("⛔️ Bu bo'lim faqat Super Admin uchun!")
        return

    admins = await get_all_admins_list()
    
    text = (
        "🛡 <b>ADMINLAR RO'YXATI</b>\n\n"
        "Hozirgi vaqtda botni boshqaruvchi shaxslar:\n\n"
    )
    
    count = 1
    for admin in admins:
        if admin['telegram_id'] != SUPER_ADMIN_ID:
            name = f"@{admin['username']}" if admin['username'] else "Noma'lum"
            joined = admin['created_at'].strftime("%d.%m.%Y") if admin['created_at'] else "Eski"
            
            text += f"{count}. 👤 <b>{name}</b>\n🆔 ID: <code>{admin['telegram_id']}</code>\n📅 Sana: {joined}\n\n"
            count += 1
            
    if count == 1:
        text += "<i>Qo'shimcha adminlar yo'q.</i>"
        
    text += "\n<i>⚠️ Super Admin (Siz) ro'yxatda ko'rinmaysiz.</i>"

    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Admin qo'shish", callback_data="admin_add_new")
    builder.button(text="➖ Admin o'chirish", callback_data="admin_delete_start")
    builder.button(text="🔙 Orqaga", callback_data="admin_back_main") 
    builder.adjust(2)

    if isinstance(message_or_call, CallbackQuery):
        await message_or_call.message.edit_text(text, reply_markup=builder.as_markup())
    else:
        await message_or_call.answer(text, reply_markup=builder.as_markup())


# ==========================================================
# 2. ADMIN QO'SHISH (Cheklovsiz)
# ==========================================================
@router.callback_query(F.data == "admin_add_new")
async def start_add_admin(call: CallbackQuery, state: FSMContext):
    # Faqat Super Admin
    if call.from_user.id != SUPER_ADMIN_ID:
        return await call.answer("Ruxsat yo'q!", show_alert=True)

    await call.message.delete()
    await call.message.answer(
        "➕ <b>YANGI ADMIN QO'SHISH</b>\n\n"
        "Yangi admin qilmoqchi bo'lgan foydalanuvchining <b>ID raqamini</b> yuboring:\n"
        "<i>Eslatma: U avval botga /start bosgan bo'lishi kerak.</i>",
        reply_markup=InlineKeyboardBuilder().button(text="🔙 Bekor qilish", callback_data="admin_cancel_action").as_markup()
    )
    await state.set_state(AdminManageState.add_new_admin_id)

@router.message(AdminManageState.add_new_admin_id)
async def save_new_admin(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("⚠️ Faqat raqamli ID kiriting!")
        return
    
    new_id = int(message.text)
    
    if new_id == message.from_user.id:
        await message.answer("😅 Siz allaqachon adminsiz.")
        return

    user = await select_user(new_id)
    if not user:
        await message.answer(
            "❌ <b>Foydalanuvchi topilmadi!</b>\n"
            "Bu odam botga hali /start bosmagan. Avval botga kirsin, keyin ID sini yuboring."
        )
        return

    username = user['username'] if user['username'] else user['full_name']

    await add_admin(new_id, username)
    
    await message.answer(f"✅ <b>Muvaffaqiyatli!</b>\n\n👤 {user['full_name']} endi adminlar safida.")
    await state.clear()
    await show_admin_list(message)


# ==========================================================
# 3. ADMIN O'CHIRISH
# ==========================================================
@router.callback_query(F.data == "admin_delete_start")
async def start_delete_admin(call: CallbackQuery):
    if call.from_user.id != SUPER_ADMIN_ID:
        return await call.answer("Ruxsat yo'q!", show_alert=True)

    admins = await get_all_admins_list()
    
    builder = InlineKeyboardBuilder()
    has_candidates = False

    for admin in admins:
        if admin['telegram_id'] != SUPER_ADMIN_ID:
            name = admin['username'] if admin['username'] else f"ID: {admin['telegram_id']}"
            builder.button(text=f"🗑 {name}", callback_data=f"del_adm_{admin['telegram_id']}")
            has_candidates = True
    
    builder.adjust(1)
    builder.button(text="🔙 Bekor qilish", callback_data="admin_cancel_action")

    if not has_candidates:
        await call.answer("O'chirish uchun boshqa adminlar yo'q.", show_alert=True)
        return

    await call.message.edit_text(
        "➖ <b>ADMINNI O'CHIRISH</b>\n\n"
        "Qaysi adminni huquqdan mahrum qilmoqchisiz? Tanlang:",
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data.startswith("del_adm_"))
async def confirm_delete_admin(call: CallbackQuery):
    target_id = int(call.data.split("_")[2])
    
    await delete_admin(target_id)
    await call.answer("✅ Admin o'chirildi!", show_alert=True)
    await show_admin_list(call)


# ==========================================================
# BEKOR QILISH
# ==========================================================
@router.callback_query(F.data == "admin_cancel_action")
async def cancel_manage_action(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await show_admin_list(call)

@router.callback_query(F.data == "admin_back_main")
async def back_to_main_panel(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("🏠 Asosiy menyu:", reply_markup=None)