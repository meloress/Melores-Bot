import pandas as pd
import io
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from openpyxl.utils import get_column_letter
from database.queries import get_dashboard_stats, get_full_users_data, get_lessons_count

router = Router()

@router.message(F.text == "📊 Statistika va Tahlil")
async def show_statistics(message: Message):
    stats = await get_dashboard_stats()
    
    total = stats['total_users'] or 0
    new_today = stats['new_today'] or 0
    remont_count = stats['funnel_remont'] or 0
    about_count = stats['funnel_about'] or 0
    zamer_count = stats['funnel_zamer'] or 0
    
    remont_percent = int((remont_count / total) * 100) if total > 0 else 0
    about_percent = int((about_count / total) * 100) if total > 0 else 0
    zamer_percent = int((zamer_count / total) * 100) if total > 0 else 0

    now = datetime.now().strftime("%d.%m.%Y | %H:%M")

    text = (
        "📊 <b>Boshqaruv Paneli (Dashboard)</b>\n"
        f"<i>📅 Sana: {now}</i>\n\n"
        
        "👥 <b>A'zolar dinamikasi:</b>\n"
        f"🟢 <b>Jami a'zolar:</b> {total} ta\n"
        f"📈 <b>Bugun qo'shildi:</b> +{new_today} ta\n"
        f"📉 <b>Bloklaganlar (Churn):</b> 0 ta (0%)\n\n"
        
        "🌪 <b>Savdo Voronkasi (Funnel):</b>\n"
        "1️⃣ <b>🏠 Yangi uylar:</b> 100% (Barcha a'zolar)\n"
        f"2️⃣ <b>🏚 Remont bo'limi:</b> {remont_percent}% ({remont_count})\n"
        f"3️⃣ <b>ℹ️ Biz haqimizda:</b> {about_percent}% ({about_count})\n"
        f"4️⃣ <b>📏 Zamer bosqichi:</b> {zamer_percent}% ({zamer_count}) — <i>🔥 Hot Leads!</i>"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Yangilash", callback_data="refresh_stats")
    builder.button(text="📥 Excelga yuklash", callback_data="download_excel_stats")
    builder.adjust(1)

    await message.answer(text, reply_markup=builder.as_markup())


# --- YANGILASH TUGMASI ---
@router.callback_query(F.data == "refresh_stats")
async def refresh_statistics(call: CallbackQuery):
    await call.message.delete()
    await show_statistics(call.message)


# --- EXCELGA YUKLASH ---
@router.callback_query(F.data == "download_excel_stats")
async def download_excel(call: CallbackQuery):
    await call.answer("⏳ Fayl tayyorlanmoqda...", show_alert=False)
    
    rows = await get_full_users_data()       
    totals = await get_lessons_count()       
    if not rows:
        await call.message.answer("📂 Baza hozircha bo'sh.")
        return

    total_lessons = totals['lessons'] 
    total_remont = totals['remont']   
    total_about = totals['about']     
    data = [dict(row) for row in rows]
    df = pd.DataFrame(data)
    
    # -------------------------------------------------------------------------
    # 3. MANTIQ: FOIZLARNI HISOBLASH VA FORMATLASH
    # -------------------------------------------------------------------------
    
    def format_progress(current_val, max_val):
        if max_val == 0: return "0% (0)"
        current_val = int(current_val)
        if current_val > max_val: current_val = max_val
            
        percent = int((current_val / max_val) * 100)
        return f"{percent}% ({current_val})"

    # A) Yangi uylar
    df['last_lesson_id'] = df['last_lesson_id'].apply(lambda x: format_progress(x, total_lessons))
    
    # B) Remont
    df['last_remont_id'] = df['last_remont_id'].apply(lambda x: format_progress(x, total_remont))
    
    # C) Biz haqimizda
    df['last_about_id'] = df['last_about_id'].apply(lambda x: format_progress(x, total_about))
    
    # D) Zamer (Bu shunchaki Ha/Yo'q)
    df['zamer_requested'] = df['zamer_requested'].apply(lambda x: "✅ HA" if x else "❌ YO'Q")

    # E) Sana
    if 'created_at' in df.columns:
        df['created_at'] = df['created_at'].astype(str).str[:16] # 2024-10-12 14:30
    df = df.rename(columns={
        "telegram_id": "Telegram ID",
        "full_name": "Ism Familiya",
        "phone": "Telefon",
        "region": "Hudud",
        "created_at": "Qo'shilgan vaqt",
        "last_lesson_id": "🏠 Yangi uylar",
        "last_remont_id": "🏚 Remont bo'limi",
        "last_about_id": "ℹ️ Biz haqimizda",
        "zamer_requested": "📏 Zamer bosganmi?"
    })
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Users')
        
        worksheet = writer.sheets['Users']
        
        for i, column in enumerate(df.columns):
            max_len = max(
                df[column].astype(str).map(len).max(),
                len(column)
            )
            worksheet.column_dimensions[get_column_letter(i + 1)].width = max_len + 3

    output.seek(0)
    
    filename = f"Hisobot_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    file = BufferedInputFile(output.read(), filename=filename)
    
    await call.message.answer_document(
        document=file, 
        caption=(
            f"📊 <b>Mukammal hisobot tayyor!</b>\n\n"
            f"🎥 <b>Bazada jami videolar:</b>\n"
            f"• Yangi uylar: {total_lessons} ta\n"
            f"• Remont: {total_remont} ta\n"
            f"• Biz haqimizda: {total_about} ta"
        )
    )