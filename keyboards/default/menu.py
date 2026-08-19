from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🏠 Янги уй учун"),
            KeyboardButton(text="🛠️  Ремонт кетяпти"),
        ],
        [
            KeyboardButton(text="📚 Каталог"),
        ],
        [
            KeyboardButton(text="ℹ️ Биз ҳақимизда"),
            KeyboardButton(text="📐 Замер белгилаш"),
        ],
        [
            KeyboardButton(text="📞 Алоқа"),
        ],
    ],
    resize_keyboard=True
)