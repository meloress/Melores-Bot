from aiogram import Router, F
from aiogram.types import Message

router = Router()

ADMIN_PHONE_NUMBER = "+998712006664" 

@router.message(F.text == "📞 Алоқа")
async def show_contact(message: Message):
    await message.answer(
        f"📞 <b>Биз билан боғланиш</b>\n\n"
        f"Саволларингиз бўлса, қуйидаги рақамга мурожаат қилишиңиз мумкин:\n\n"
        f"👇 <b>Рақам:</b>\n"
        f"<code>{ADMIN_PHONE_NUMBER}</code>"
    )

    await message.answer_contact(
        phone_number=ADMIN_PHONE_NUMBER,
        first_name="Мелорес",  
    )