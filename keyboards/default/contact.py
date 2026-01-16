from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def request_phone_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Tugmani bosing yoki raqam yozing..."
    )