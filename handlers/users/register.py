from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from database.queries import db
from keyboards.default.menu import main_menu # O'zingiz yaratasiz
from states.registration import RegisterState # State klassingiz

router = Router()

# ... Ism va Telefon handlers bu yerda bo'ladi ...

@router.callback_query(RegisterState.region)
async def region_selected(call: types.CallbackQuery, state: FSMContext):
    region = call.data # Viloyat nomi
    user_id = call.from_user.id
    
    # Bazaga yozamiz
    await db.update_user_data(user_id, region=region)
    
    # 1. Bot haqida videoxabar (Note)
    # File ID ni oldindan olib qo'ygan bo'lishingiz kerak yoki hardcode qilasiz
    intro_video_note_id = "BQACAgIAAxkBAAI..." 
    await call.message.answer_video_note(intro_video_note_id)
    
    # 2. Asosiy menyu
    await call.message.answer(
        "Ro'yxatdan o'tish muvaffaqiyatli yakunlandi! Quyidagi bo'limlardan birini tanlang:",
        reply_markup=main_menu
    )
    await state.clear()