from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# 1. SUPER ADMIN MENYUSI (To'liq, Admin boshqaruvi BOR)
super_admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📊 Statistika va Tahlil"),
            KeyboardButton(text="👥 Foydalanuvchilar (CRM)"),
        ],
        [
            KeyboardButton(text="📨 Xabar yuborish"),
            KeyboardButton(text="👮‍♂️ Adminlar boshqaruvi"), 
        ],
    ],
    resize_keyboard=True
)

# 2. ODDIY ADMIN MENYUSI (Admin boshqaruvi YO'Q)
regular_admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📊 Statistika va Tahlil"),
            KeyboardButton(text="👥 Foydalanuvchilar (CRM)"),
        ],
        [
            KeyboardButton(text="📨 Xabar yuborish"),
        ],
    ],
    resize_keyboard=True
)