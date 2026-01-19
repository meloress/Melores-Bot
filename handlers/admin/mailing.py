import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from database.queries import (
    get_active_users, get_users_by_region, 
    get_users_by_zamer, get_users_by_remont_interest,
    add_template, get_all_templates, get_template, delete_template
)
from states.registration import AdminMailingState

router = Router()

# --- VILOYATLAR RO'YXATI ---
REGIONS = {
    "toshkent_sh": "📍 Toshkent shahri",
    "toshkent_vil": "📍 Toshkent viloyati",
    "andijon": "📍 Andijon viloyati",
    "fargona": "📍 Farg'ona viloyati",
    "namangan": "📍 Namangan viloyati",
    "sirdaryo": "📍 Sirdaryo viloyati",
    "jizzax": "📍 Jizzax viloyati",
    "samarqand": "📍 Samarqand viloyati",
    "buxoro": "📍 Buxoro viloyati",
    "navoiy": "📍 Navoiy viloyati",
    "qashqadaryo": "📍 Qashqadaryo viloyati",
    "surxondaryo": "📍 Surxondaryo viloyati",
    "xorazm": "📍 Xorazm viloyati",
    "qoraqalpogiston": "📍 Qoraqalpog'iston Respublikasi",
}

# ==========================================================
# 1. ASOSIY MAILING MENYUSI
# ==========================================================
async def show_mailing_menu(message_or_call):
    text = (
        "🚀 <b>REKLAMA VA XABARNOMALAR</b>\n\n"
        "Kimga xabar yubormoqchisiz? Maqsadli auditoriyani tanlang.\n"
        "<i>Eslatma: Xabar ichida rasm, video, tekst va URL tugmalar bo'lishi mumkin.</i>"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📢 Barchaga (Broadcast)", callback_data="mail_broadcast")
    builder.button(text="🎯 Target (Hudud/Bosqich)", callback_data="mail_target")
    builder.button(text="👤 Yakkama-yakka (ID)", callback_data="mail_private")
    builder.button(text="💾 Saqlangan shablonlar", callback_data="mail_templates_list")
    builder.adjust(2)

    if isinstance(message_or_call, CallbackQuery):
        await message_or_call.message.edit_text(text, reply_markup=builder.as_markup())
    else:
        await message_or_call.answer(text, reply_markup=builder.as_markup())

@router.callback_query(F.data == "mail_back_menu")
async def back_to_mailing_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await show_mailing_menu(call)

# ==========================================================
# 2. XABAR TURLARI VA TARGETLASH
# ==========================================================

# A) 📢 Barchaga
@router.callback_query(F.data == "mail_broadcast")
async def start_broadcast(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "📢 <b>BARCHAGA XABAR YUBORISH</b>\n\n"
        "✍️ <i>Yubormoqchi bo'lgan xabaringizni kiriting (Matn, Rasm, Video):</i>",
        reply_markup=InlineKeyboardBuilder().button(text="🔙 Orqaga", callback_data="mail_back_menu").as_markup()
    )
    await state.update_data(target_type="all")
    await state.set_state(AdminMailingState.msg_content)

# B) 🎯 Target (Kategoriyalar)
@router.callback_query(F.data == "mail_target")
async def start_target(call: CallbackQuery):
    text = "🎯 <b>KIMGA YUBORMOQCHISIZ?</b>\nAuditoriyani tanlang:"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📍 Toshkent shahri", callback_data="target_region_toshkent_sh")
    builder.button(text="🏙 Viloyatlar", callback_data="mail_select_regions_list")
    builder.button(text="📏 Zamer so'raganlar", callback_data="target_zamer")
    builder.button(text="🏚 Remontga qiziqqanlar", callback_data="target_remont_active")
    builder.button(text="🔙 Orqaga", callback_data="mail_back_menu")
    builder.adjust(1) 
    
    await call.message.edit_text(text, reply_markup=builder.as_markup())

# C) Viloyatlar ro'yxatini chiqarish
@router.callback_query(F.data == "mail_select_regions_list")
async def show_regions_list(call: CallbackQuery):
    text = "🏙 <b>QAYSI VILOYATGA YUBORMOQCHISIZ?</b>\nTanlang:"
    
    builder = InlineKeyboardBuilder()
    for key, value in REGIONS.items():
        if key != "toshkent_sh":
            builder.button(text=value, callback_data=f"target_region_{key}")
            
    builder.adjust(2) 
    builder.button(text="🔙 Orqaga", callback_data="mail_target")
    
    await call.message.edit_text(text, reply_markup=builder.as_markup())

# Target tanlanganda
@router.callback_query(F.data.startswith("target_"))
async def target_selected(call: CallbackQuery, state: FSMContext):
    selection = call.data.replace("target_", "") 
    
    display_name = selection.upper()
    if selection.startswith("region_"):
        code = selection.replace("region_", "")
        display_name = REGIONS.get(code, code).upper()
    elif selection == "zamer": display_name = "ZAMER SO'RAGANLAR"
    elif selection == "remont_active": display_name = "REMONTGA QIZIQQANLAR"

    await call.message.edit_text(
        f"✅ <b>Auditoriya tanlandi:</b>\n👉 {display_name}\n\n"
        "✍️ <i>Endi xabar matnini yoki rasmini yuboring:</i>",
        reply_markup=InlineKeyboardBuilder().button(text="🔙 Orqaga", callback_data="mail_target").as_markup()
    )
    await state.update_data(target_type=selection)
    await state.set_state(AdminMailingState.msg_content)

# D) 👤 Private
@router.callback_query(F.data == "mail_private")
async def start_private(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "👤 <b>Foydalanuvchi ID sini kiriting:</b>",
        reply_markup=InlineKeyboardBuilder().button(text="🔙 Orqaga", callback_data="mail_back_menu").as_markup()
    )
    await state.set_state(AdminMailingState.private_id)

@router.message(AdminMailingState.private_id)
async def get_private_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("⚠️ Faqat raqamli ID kiriting!")
        return
    
    await state.update_data(target_type="private", target_id=int(message.text))
    await message.answer("✍️ <b>Xabarni yuboring:</b>")
    await state.set_state(AdminMailingState.msg_content)


# ==========================================================
# 3. SHABLONLAR TIZIMI
# ==========================================================

@router.callback_query(F.data == "mail_templates_list")
async def show_templates(call: CallbackQuery):
    templates = await get_all_templates()
    
    if not templates:
        await call.answer("📂 Shablonlar yo'q.", show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    for tmp in templates:
        builder.button(text=f"📄 {tmp['name']}", callback_data=f"use_template_{tmp['id']}")
    
    builder.button(text="🔙 Orqaga", callback_data="mail_back_menu")
    builder.adjust(1)
    
    await call.message.edit_text("💾 <b>Saqlangan shablonlar:</b>\nFoydalanish uchun ustiga bosing:", reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("use_template_"))
async def select_template(call: CallbackQuery, state: FSMContext):
    temp_id = int(call.data.split("_")[2])
    template = await get_template(temp_id)
    
    if not template:
        await call.answer("Xatolik: Shablon topilmadi", show_alert=True)
        return

    await state.update_data(
        template_mode=True,
        msg_type=template['msg_type'],
        file_id=template['file_id'],
        caption=template['caption']
    )
    
    text = f"✅ <b>Shablon tanlandi:</b> {template['name']}\n\n🎯 <b>Kimga yuboramiz?</b>"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📢 Barchaga", callback_data="temp_target_all")
    builder.button(text="📍 Toshkent shahri", callback_data="temp_target_region_toshkent_sh")
    builder.button(text="🗑 Shablonni o'chirish", callback_data=f"del_template_{temp_id}")
    builder.button(text="🔙 Bekor qilish", callback_data="mail_templates_list")
    builder.adjust(1)
    
    await call.message.edit_text(text, reply_markup=builder.as_markup())

# Shablon uchun targetlar
@router.callback_query(F.data.startswith("temp_target_"))
async def template_target_selected(call: CallbackQuery, state: FSMContext):
    target = call.data.replace("temp_target_", "")
    await state.update_data(target_type=target)
    await show_preview(call.message, state)

@router.callback_query(F.data.startswith("del_template_"))
async def remove_template(call: CallbackQuery):
    temp_id = int(call.data.split("_")[2])
    await delete_template(temp_id)
    await call.answer("🗑 Shablon o'chirildi!", show_alert=True)
    await show_templates(call)


# ==========================================================
# 4. XABARNI QABUL QILISH VA PREVIEW
# ==========================================================
@router.message(AdminMailingState.msg_content)
async def receive_content(message: Message, state: FSMContext):
    msg_type = "text"
    file_id = None
    caption = message.text or message.caption
    
    if message.photo:
        msg_type = "photo"
        file_id = message.photo[-1].file_id
    elif message.video:
        msg_type = "video"
        file_id = message.video.file_id
    elif message.animation:
        msg_type = "video"
        file_id = message.animation.file_id

    await state.update_data(
        msg_type=msg_type,
        file_id=file_id,
        caption=caption,
        msg_id=message.message_id,
        from_chat_id=message.chat.id
    )
    
    await show_preview(message, state)

async def show_preview(message_obj, state: FSMContext):
    data = await state.get_data()
    
    await message_obj.answer("👁 <b>KO'RIB CHIQISH (PREVIEW):</b>")
    
    try:
        if data.get('template_mode'):
            if data['msg_type'] == 'text':
                await message_obj.answer(data['caption'])
            elif data['msg_type'] == 'photo':
                await message_obj.answer_photo(photo=data['file_id'], caption=data['caption'])
            elif data['msg_type'] == 'video':
                await message_obj.answer_video(video=data['file_id'], caption=data['caption'])
        else:
            await message_obj.bot.copy_message(
                chat_id=message_obj.chat.id,
                from_chat_id=data['from_chat_id'],
                message_id=data['msg_id']
            )
    except Exception as e:
        await message_obj.answer(f"⚠️ Media xatolik: {e}")

    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 YUBORISH", callback_data="confirm_send_mail")
    
    if not data.get('template_mode'):
        builder.button(text="💾 Shablon qilib saqlash", callback_data="ask_save_template")
        
    builder.button(text="❌ Bekor qilish", callback_data="mail_back_menu")
    builder.adjust(1)
    
    # ⚠️ XATOLIKNI OLDINI OLISH UCHUN TEKSHIRUV
    target = data.get('target_type')
    if not target:
        target_name = "⚠️ Noma'lum"
    elif target.startswith("region_"):
        target_name = REGIONS.get(target.replace("region_", ""), target)
    elif target == "all": target_name = "BARCHAGA"
    else: target_name = target

    await message_obj.answer(
        f"📊 <b>Tayyor!</b>\n🎯 Auditoriya: <b>{target_name}</b>\nTasdiqlaysizmi?",
        reply_markup=builder.as_markup()
    )


# ==========================================================
# 5. SHABLON QILIB SAQLASH
# ==========================================================
@router.callback_query(F.data == "ask_save_template")
async def ask_template_name(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("📝 <b>Shablon uchun nom bering:</b>\n<i>Masalan: Yangi yil tabrigi</i>")
    await state.set_state(AdminMailingState.save_template_name)

@router.message(AdminMailingState.save_template_name)
async def save_template_finish(message: Message, state: FSMContext):
    name = message.text
    data = await state.get_data()
    
    await add_template(name=name, msg_type=data['msg_type'], file_id=data['file_id'], caption=data['caption'])
    
    await message.answer(f"✅ <b>'{name}' shabloni saqlandi!</b>")
    await show_preview(message, state)


# ==========================================================
# 6. YUBORISH (FINAL LOGIKA) - XATOLIK TUZATILDI ✅
# ==========================================================
@router.callback_query(F.data == "confirm_send_mail")
async def execute_mailing(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    target_type = data.get("target_type")
    
    # ⚠️ XATOLIKNI TUZATISH: Agar target_type None bo'lsa
    if not target_type:
        await call.answer("❌ Xatolik: Kimga yuborish kerakligi aniqlanmadi!", show_alert=True)
        # Ehtimol sessiya eskirgan, menyuga qaytaramiz
        await show_mailing_menu(call)
        return
    
    users = []
    
    # 1. Auditoriyani aniqlash
    if target_type == "all":
        users = await get_active_users()
        
    elif target_type.startswith("region_"):
        region_code = target_type.replace("region_", "")
        region_full_name = REGIONS.get(region_code)
        
        if region_full_name:
            users = await get_users_by_region(region_full_name)
        
    elif target_type == "zamer":
        users = await get_users_by_zamer()
        
    elif target_type == "remont_active":
        users = await get_users_by_remont_interest()
        
    elif target_type == "private":
        users = [{'telegram_id': data.get("target_id")}] 

    if not users:
        await call.message.answer("❌ <b>Bu kategoriyada foydalanuvchilar topilmadi.</b>")
        await state.clear()
        return

    sent = 0
    blocked = 0
    status_msg = await call.message.answer(f"⏳ <b>Yuborish boshlandi...</b>\nJami: {len(users)} ta")
    
    for user in users:
        try:
            if data.get('template_mode'):
                if data['msg_type'] == 'text':
                    await call.bot.send_message(chat_id=user['telegram_id'], text=data['caption'])
                elif data['msg_type'] == 'photo':
                    await call.bot.send_photo(chat_id=user['telegram_id'], photo=data['file_id'], caption=data['caption'])
                elif data['msg_type'] == 'video':
                    await call.bot.send_video(chat_id=user['telegram_id'], video=data['file_id'], caption=data['caption'])
            else:
                await call.bot.copy_message(chat_id=user['telegram_id'], from_chat_id=data['from_chat_id'], message_id=data['msg_id'])
            
            sent += 1
            await asyncio.sleep(0.05)
        except:
            blocked += 1
    
    await status_msg.delete()
    await call.message.answer(
        f"🏁 <b>YAKUNLANDI!</b>\n✅ Bordi: {sent}\n🚫 Blok: {blocked}",
        reply_markup=InlineKeyboardBuilder().button(text="🔙 Menyuga qaytish", callback_data="mail_back_menu").as_markup()
    )
    await state.clear()